from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AIAttitude(str, Enum):
    skeptical = "skeptical"
    neutral = "neutral"
    optimistic = "optimistic"


class PersonaStatus(str, Enum):
    draft = "draft"
    active = "active"
    deprecated = "deprecated"
    archived = "archived"


class UsageGuidance(BaseModel):
    best_for: list[str] = Field(default_factory=list)
    avoid_for: list[str] = Field(default_factory=list)


class PersonaBase(BaseModel):
    slug: str
    name: str
    version: str
    summary: str
    knowledge_level: KnowledgeLevel
    ai_attitude: AIAttitude
    traits: list[str] = Field(default_factory=list)
    communication_style: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    frustrations: list[str] = Field(default_factory=list)
    prompt_template: str
    usage_guidance: UsageGuidance = Field(default_factory=UsageGuidance)
    tags: list[str] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not value:
            raise ValueError("slug is required")
        if value.lower() != value:
            raise ValueError("slug must be lowercase")
        return value

    @field_validator("traits", "communication_style", "goals", "frustrations", "tags")
    @classmethod
    def dedupe_and_trim(cls, values: list[str]) -> list[str]:
        unique: list[str] = []
        seen: set[str] = set()
        for raw in values:
            item = raw.strip()
            if not item:
                continue
            if item in seen:
                continue
            seen.add(item)
            unique.append(item)
        return unique


class PersonaCreate(PersonaBase):
    id: str
    status: PersonaStatus = PersonaStatus.draft
    changelog: str | None = None
    source_version: str | None = None


class PersonaUpdate(BaseModel):
    name: str | None = None
    summary: str | None = None
    knowledge_level: KnowledgeLevel | None = None
    ai_attitude: AIAttitude | None = None
    traits: list[str] | None = None
    communication_style: list[str] | None = None
    goals: list[str] | None = None
    frustrations: list[str] | None = None
    prompt_template: str | None = None
    usage_guidance: UsageGuidance | None = None
    tags: list[str] | None = None
    changelog: str | None = None


class PersonaRecord(PersonaBase):
    id: str
    status: PersonaStatus
    changelog: str | None = None
    source_version: str | None = None
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    created_by: str = "system"
    is_latest: bool = False


class PersonasListResponse(BaseModel):
    items: list[PersonaRecord]
    next_cursor: str | None = None
    count: int


class BulkImportRequest(BaseModel):
    personas: list[PersonaCreate]


class BulkImportItemResult(BaseModel):
    id: str
    created: bool
    error: str | None = None


class BulkImportResponse(BaseModel):
    created: int
    failed: int
    skipped: int
    results: list[BulkImportItemResult]


class TransitionRequest(BaseModel):
    reason: str | None = None
    actor: str = "system"


class ApiErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiErrorEnvelope(BaseModel):
    error: ApiErrorPayload


class RosterItem(BaseModel):
    slug: str
    version_selector: str
    role: str
    business_function: str | None = None
    task_type: str | None = None


class RosterCreate(BaseModel):
    id: str
    name: str
    items: list[RosterItem] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RosterUpdate(BaseModel):
    name: str | None = None
    items: list[RosterItem] | None = None
    tags: list[str] | None = None


class RosterRecord(BaseModel):
    id: str
    name: str
    items: list[RosterItem]
    tags: list[str]
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    created_by: str = "system"


class EvaluationTarget(BaseModel):
    type: str
    slug: str | None = None
    version_selector: str | None = None
    roster_id: str | None = None


class EvaluationInput(BaseModel):
    task: str
    context: str | None = None


class EvaluationOptions(BaseModel):
    record_transcript: bool = True
    max_tokens: int = 1200
    scoring_mode: str = "hybrid_weighted"
    weights: dict[str, float] = Field(default_factory=lambda: {"automated": 0.6, "human": 0.4})


class EvaluationCreateRequest(BaseModel):
    target: EvaluationTarget
    input: EvaluationInput
    options: EvaluationOptions = Field(default_factory=EvaluationOptions)


class EvaluationRecord(BaseModel):
    id: str
    status: str
    target: EvaluationTarget
    input: EvaluationInput
    options: EvaluationOptions
    score_automated: float
    score_human: float
    score_total: float
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)


class EvaluationCompareRequest(BaseModel):
    evaluation_ids: list[str]


class EvaluationCompareResult(BaseModel):
    evaluation_id: str
    score_total: float
    score_automated: float
    score_human: float


class EvaluationCompareResponse(BaseModel):
    items: list[EvaluationCompareResult]
