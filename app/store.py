from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from sqlmodel import Session, select

from app.models import EvaluationModel, PersonaModel, RosterModel
from app.schemas import (
    EvaluationCompareResult,
    EvaluationCreateRequest,
    EvaluationRecord,
    PersonaCreate,
    PersonaRecord,
    PersonaStatus,
    PersonaUpdate,
    RosterCreate,
    RosterRecord,
    RosterUpdate,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError("version must be MAJOR.MINOR.PATCH")
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as exc:
        raise ValueError("version must be MAJOR.MINOR.PATCH") from exc


@dataclass
class TransitionRule:
    from_status: PersonaStatus
    to_status: PersonaStatus


TRANSITIONS: tuple[TransitionRule, ...] = (
    TransitionRule(PersonaStatus.draft, PersonaStatus.active),
    TransitionRule(PersonaStatus.active, PersonaStatus.deprecated),
    TransitionRule(PersonaStatus.deprecated, PersonaStatus.archived),
)


class PersonaStore:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def _persona_record_from_model(self, row: PersonaModel) -> PersonaRecord:
        return PersonaRecord.model_validate(row.model_dump())

    def _roster_record_from_model(self, row: RosterModel) -> RosterRecord:
        return RosterRecord.model_validate(row.model_dump())

    def _evaluation_record_from_model(self, row: EvaluationModel) -> EvaluationRecord:
        return EvaluationRecord.model_validate(row.model_dump())

    def _ensure_unique(self, session: Session, persona: PersonaCreate) -> None:
        if session.get(PersonaModel, persona.id):
            raise ValueError("ID_ALREADY_EXISTS")
        existing = session.exec(
            select(PersonaModel).where(PersonaModel.slug == persona.slug, PersonaModel.version == persona.version)
        ).first()
        if existing:
            raise ValueError("SLUG_VERSION_ALREADY_EXISTS")

    def create(self, persona: PersonaCreate, created_by: str = "system") -> PersonaRecord:
        parse_semver(persona.version)
        with self._session_factory() as session:
            self._ensure_unique(session, persona)
            timestamp = utc_now()
            row = PersonaModel(
                **persona.model_dump(mode="json"),
                created_by=created_by,
                created_at=timestamp,
                updated_at=timestamp,
            )
            session.add(row)
            session.commit()
            self._recompute_latest_flags(session, row.slug)
            session.refresh(row)
            return self._persona_record_from_model(row)

    def list(
        self,
        slug: str | None = None,
        status: PersonaStatus | None = None,
        tag: str | None = None,
        ai_attitude: str | None = None,
        knowledge_level: str | None = None,
        q: str | None = None,
    ) -> list[PersonaRecord]:
        with self._session_factory() as session:
            records = [self._persona_record_from_model(row) for row in session.exec(select(PersonaModel)).all()]
        if slug:
            records = [item for item in records if item.slug == slug]
        if status:
            records = [item for item in records if item.status == status]
        if tag:
            records = [item for item in records if tag in item.tags]
        if ai_attitude:
            records = [item for item in records if item.ai_attitude == ai_attitude]
        if knowledge_level:
            records = [item for item in records if item.knowledge_level == knowledge_level]
        if q:
            query = q.lower()
            records = [
                item
                for item in records
                if query in item.name.lower()
                or query in item.summary.lower()
                or query in item.slug.lower()
            ]
        records.sort(key=lambda value: (value.slug, parse_semver(value.version), value.id), reverse=True)
        return records

    def get_by_id(self, persona_id: str) -> PersonaRecord | None:
        with self._session_factory() as session:
            row = session.get(PersonaModel, persona_id)
            return self._persona_record_from_model(row) if row else None

    def get_versions(self, slug: str) -> list[PersonaRecord]:
        with self._session_factory() as session:
            rows = session.exec(select(PersonaModel).where(PersonaModel.slug == slug)).all()
        records = [self._persona_record_from_model(row) for row in rows]
        records.sort(key=lambda value: parse_semver(value.version), reverse=True)
        return records

    def get_by_slug_version(self, slug: str, version: str) -> PersonaRecord | None:
        for item in self.get_versions(slug):
            if item.version == version:
                return item
        return None

    def get_latest(self, slug: str) -> PersonaRecord | None:
        versions = self.get_versions(slug)
        candidates = [
            item
            for item in versions
            if item.status in {PersonaStatus.active, PersonaStatus.deprecated, PersonaStatus.archived}
        ]
        return candidates[0] if candidates else None

    def update_draft(self, persona_id: str, update: PersonaUpdate) -> PersonaRecord:
        with self._session_factory() as session:
            row = session.get(PersonaModel, persona_id)
            if not row:
                raise KeyError("NOT_FOUND")
            if row.status != PersonaStatus.draft:
                raise ValueError("ONLY_DRAFT_EDITABLE")
            updates = update.model_dump(exclude_unset=True, mode="json")
            for field_name, value in updates.items():
                setattr(row, field_name, value)
            row.updated_at = utc_now()
            session.add(row)
            session.commit()
            self._recompute_latest_flags(session, row.slug)
            session.refresh(row)
            return self._persona_record_from_model(row)

    def transition(self, persona_id: str, to_status: PersonaStatus) -> PersonaRecord:
        with self._session_factory() as session:
            row = session.get(PersonaModel, persona_id)
            if not row:
                raise KeyError("NOT_FOUND")
            allowed = any(rule.from_status == row.status and rule.to_status == to_status for rule in TRANSITIONS)
            if not allowed:
                raise ValueError("INVALID_STATUS_TRANSITION")
            row.status = to_status.value
            row.updated_at = utc_now()
            session.add(row)
            session.commit()
            self._recompute_latest_flags(session, row.slug)
            session.refresh(row)
            return self._persona_record_from_model(row)

    def delete_draft(self, persona_id: str) -> None:
        with self._session_factory() as session:
            row = session.get(PersonaModel, persona_id)
            if not row:
                raise KeyError("NOT_FOUND")
            if row.status != PersonaStatus.draft:
                raise ValueError("ONLY_DRAFT_DELETABLE")
            slug = row.slug
            session.delete(row)
            session.commit()
            self._recompute_latest_flags(session, slug)

    def _recompute_latest_flags(self, session: Session, slug: str) -> None:
        rows = session.exec(select(PersonaModel).where(PersonaModel.slug == slug)).all()
        versions = [self._persona_record_from_model(row) for row in rows]
        if not versions:
            return
        latest = None
        for item in versions:
            if item.status != PersonaStatus.draft:
                latest = item
                break
        latest_id = latest.id if latest else None
        for row in rows:
            row.is_latest = latest_id is not None and row.id == latest_id
            session.add(row)
        session.commit()

    def create_roster(self, roster: RosterCreate, created_by: str = "system") -> RosterRecord:
        with self._session_factory() as session:
            if session.get(RosterModel, roster.id):
                raise ValueError("ROSTER_ID_ALREADY_EXISTS")
            timestamp = utc_now()
            row = RosterModel(
                **roster.model_dump(mode="json"),
                created_at=timestamp,
                updated_at=timestamp,
                created_by=created_by,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._roster_record_from_model(row)

    def list_rosters(self) -> list[RosterRecord]:
        with self._session_factory() as session:
            return [self._roster_record_from_model(row) for row in session.exec(select(RosterModel)).all()]

    def get_roster(self, roster_id: str) -> RosterRecord | None:
        with self._session_factory() as session:
            row = session.get(RosterModel, roster_id)
            return self._roster_record_from_model(row) if row else None

    def update_roster(self, roster_id: str, update: RosterUpdate) -> RosterRecord:
        with self._session_factory() as session:
            row = session.get(RosterModel, roster_id)
            if not row:
                raise KeyError("NOT_FOUND")
            updates = update.model_dump(exclude_unset=True, mode="json")
            for field_name, value in updates.items():
                setattr(row, field_name, value)
            row.updated_at = utc_now()
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._roster_record_from_model(row)

    def delete_roster(self, roster_id: str) -> None:
        with self._session_factory() as session:
            row = session.get(RosterModel, roster_id)
            if not row:
                raise KeyError("NOT_FOUND")
            session.delete(row)
            session.commit()

    def create_evaluation(self, request: EvaluationCreateRequest) -> EvaluationRecord:
        target = request.target
        if target.type == "persona":
            if not target.slug:
                raise ValueError("INVALID_TARGET")
            selector = target.version_selector or "latest"
            record = self.get_latest(target.slug) if selector == "latest" else self.get_by_slug_version(target.slug, selector)
            if not record:
                raise ValueError("TARGET_NOT_FOUND")
        elif target.type == "roster":
            if not target.roster_id or not self.get_roster(target.roster_id):
                raise ValueError("TARGET_NOT_FOUND")
        else:
            raise ValueError("INVALID_TARGET")

        automated = 0.82
        human = 0.76
        weights = request.options.weights
        total = automated * weights.get("automated", 0.6) + human * weights.get("human", 0.4)
        timestamp = utc_now()
        with self._session_factory() as session:
            row = EvaluationModel(
                id=f"eval_{uuid4().hex[:10]}",
                status="completed",
                target=request.target.model_dump(mode="json"),
                input=request.input.model_dump(mode="json"),
                options=request.options.model_dump(mode="json"),
                score_automated=round(automated, 4),
                score_human=round(human, 4),
                score_total=round(total, 4),
                created_at=timestamp,
                updated_at=timestamp,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._evaluation_record_from_model(row)

    def get_evaluation(self, evaluation_id: str) -> EvaluationRecord | None:
        with self._session_factory() as session:
            row = session.get(EvaluationModel, evaluation_id)
            return self._evaluation_record_from_model(row) if row else None

    def compare_evaluations(self, evaluation_ids: list[str]) -> list[EvaluationCompareResult]:
        results: list[EvaluationCompareResult] = []
        with self._session_factory() as session:
            rows = session.exec(select(EvaluationModel).where(EvaluationModel.id.in_(evaluation_ids))).all()
        by_id = {row.id: row for row in rows}
        for evaluation_id in evaluation_ids:
            row = by_id.get(evaluation_id)
            if not row:
                continue
            results.append(
                EvaluationCompareResult(
                    evaluation_id=row.id,
                    score_total=row.score_total,
                    score_automated=row.score_automated,
                    score_human=row.score_human,
                )
            )
        results.sort(key=lambda item: item.score_total, reverse=True)
        return results
