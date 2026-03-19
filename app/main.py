from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_session_factory
from app.schemas import (
    ApiErrorEnvelope,
    BulkImportItemResult,
    BulkImportRequest,
    BulkImportResponse,
    EvaluationCompareRequest,
    EvaluationCompareResponse,
    EvaluationCreateRequest,
    EvaluationRecord,
    PersonaCreate,
    PersonaRecord,
    PersonasListResponse,
    PersonaStatus,
    PersonaUpdate,
    RosterCreate,
    RosterRecord,
    RosterUpdate,
    TransitionRequest,
)
from app.store import PersonaStore


TRY_CLOUDFLARE_PATTERN = re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")


def api_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ApiErrorEnvelope(error={"code": code, "message": message, "details": details or {}}).model_dump(),
    )


def get_store(request: Request) -> PersonaStore:
    return request.app.state.store


def is_port_open(host: str = "127.0.0.1", port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def reload_trigger_path() -> Path:
    return Path(__file__).with_name("reload_trigger.py")


def write_reload_trigger() -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    reload_trigger_path().write_text(f'STAMP = "{timestamp}"\n', encoding="utf-8")


def launch_server_process() -> None:
    root = project_root()
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    python_executable = str(venv_python if venv_python.exists() else Path(sys.executable))
    command = [python_executable, "-m", "uvicorn", "app.main:app", "--reload"]
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        command,
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )


def resolve_cloudflared_path(explicit_path: str | None = None) -> str | None:
    candidates: list[str] = []
    if explicit_path:
        candidates.append(explicit_path)

    env_path = os.getenv("CLOUDFLARED_PATH")
    if env_path:
        candidates.append(env_path)

    which_path = shutil.which("cloudflared")
    if which_path:
        candidates.append(which_path)

    candidates.extend(
        [
            r"C:\Program Files\cloudflared\cloudflared.exe",
            r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        ]
    )

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def _drain_process_output(process: subprocess.Popen[str]) -> None:
    if process.stdout is None:
        return
    for _ in process.stdout:
        pass


def start_cloudflare_tunnel(target_url: str) -> tuple[subprocess.Popen[str], str]:
    cloudflared_path = resolve_cloudflared_path()
    if not cloudflared_path:
        raise ValueError("CLOUDFLARED_NOT_FOUND")

    command = [cloudflared_path, "tunnel", "--url", target_url]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(project_root()),
    )

    public_url = ""
    deadline = time.time() + 20
    while time.time() < deadline and process.poll() is None:
        if process.stdout is None:
            break
        line = process.stdout.readline()
        if not line:
            continue
        match = TRY_CLOUDFLARE_PATTERN.search(line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        process.terminate()
        raise RuntimeError("CLOUDFLARE_URL_NOT_FOUND")

    drain_thread = threading.Thread(target=_drain_process_output, args=(process,), daemon=True)
    drain_thread.start()

    return process, public_url


def create_app(database_url: str | None = None) -> FastAPI:
    _, session_factory = create_session_factory(database_url)
    app = FastAPI(title="Persona Registry API", version="0.2.0")
    app.state.store = PersonaStore(session_factory)
    app.state.api_key = os.getenv("PERSONA_REGISTRY_API_KEY", "").strip()
    app.state.tunnel_url = ""
    app.state.tunnel_target_url = "http://127.0.0.1:8000"
    app.state.tunnel_process = None

    # Enable CORS for local development and testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_api_key(request: Request, call_next):
        configured_key: str = request.app.state.api_key
        if not configured_key:
            return await call_next(request)

        if not request.url.path.startswith("/v1"):
            return await call_next(request)

        provided_key = request.headers.get("x-api-key", "")
        if provided_key != configured_key:
            from fastapi.responses import JSONResponse

            payload = ApiErrorEnvelope(
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Missing or invalid API key",
                    "details": {},
                }
            ).model_dump()
            return JSONResponse(status_code=401, content={"detail": payload})

        return await call_next(request)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/admin/server/start")
    def start_server() -> dict[str, str | bool]:
        if is_port_open():
            return {"ok": True, "status": "already_running"}
        launch_server_process()
        return {"ok": True, "status": "started"}

    @app.post("/v1/admin/server/reload")
    def reload_server() -> dict[str, str | bool]:
        write_reload_trigger()
        return {"ok": True, "status": "reload_requested"}

    @app.post("/v1/admin/tunnel/start")
    def start_tunnel(request: Request, target_url: str = Query(default="http://127.0.0.1:8000")) -> dict[str, str | bool]:
        try:
            current_process = request.app.state.tunnel_process
            if current_process is not None and current_process.poll() is None and request.app.state.tunnel_url:
                return {
                    "ok": True,
                    "status": "already_running",
                    "url": request.app.state.tunnel_url,
                    "target_url": request.app.state.tunnel_target_url,
                }

            process, public_url = start_cloudflare_tunnel(target_url)
            request.app.state.tunnel_process = process
            request.app.state.tunnel_url = public_url
            request.app.state.tunnel_target_url = target_url
            return {
                "ok": True,
                "status": "started",
                "url": public_url,
                "target_url": target_url,
            }
        except ValueError as exc:
            if str(exc) == "CLOUDFLARED_NOT_FOUND":
                raise api_error(500, "CLOUDFLARED_NOT_FOUND", "Could not find cloudflared executable") from exc
            raise api_error(500, "TUNNEL_START_FAILED", "Failed to start Cloudflare tunnel") from exc
        except RuntimeError as exc:
            if str(exc) == "CLOUDFLARE_URL_NOT_FOUND":
                raise api_error(500, "CLOUDFLARE_URL_NOT_FOUND", "Tunnel started but no public URL was detected") from exc
            raise api_error(500, "TUNNEL_START_FAILED", "Failed to start Cloudflare tunnel") from exc

    @app.post("/v1/admin/tunnel/stop")
    def stop_tunnel(request: Request) -> dict[str, str | bool]:
        process = request.app.state.tunnel_process
        if process is None or process.poll() is not None:
            request.app.state.tunnel_process = None
            return {
                "ok": True,
                "status": "already_stopped",
                "url": request.app.state.tunnel_url,
                "target_url": request.app.state.tunnel_target_url,
            }

        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        request.app.state.tunnel_process = None
        request.app.state.tunnel_url = ""
        return {
            "ok": True,
            "status": "stopped",
            "url": "",
            "target_url": request.app.state.tunnel_target_url,
        }

    @app.get("/v1/admin/tunnel/status")
    def tunnel_status(request: Request) -> dict[str, str | bool]:
        process = request.app.state.tunnel_process
        is_running = bool(process is not None and process.poll() is None)

        if is_running and request.app.state.tunnel_url:
            return {
                "ok": True,
                "status": "running",
                "url": request.app.state.tunnel_url,
                "target_url": request.app.state.tunnel_target_url,
                "running": True,
            }

        if request.app.state.tunnel_url:
            return {
                "ok": True,
                "status": "stopped",
                "url": request.app.state.tunnel_url,
                "target_url": request.app.state.tunnel_target_url,
                "running": False,
            }

        return {
            "ok": True,
            "status": "unknown",
            "url": "",
            "target_url": request.app.state.tunnel_target_url,
            "running": False,
        }

    @app.post("/v1/personas", response_model=PersonaRecord)
    def create_persona(request: Request, persona: PersonaCreate, created_by: str = Query(default="system")) -> PersonaRecord:
        if persona.status != PersonaStatus.draft:
            raise api_error(400, "INVALID_INITIAL_STATUS", "Only draft status is allowed at create")
        try:
            return get_store(request).create(persona, created_by=created_by)
        except ValueError as exc:
            if str(exc) == "ID_ALREADY_EXISTS":
                raise api_error(409, "ID_ALREADY_EXISTS", "Persona ID already exists") from exc
            if str(exc) == "SLUG_VERSION_ALREADY_EXISTS":
                raise api_error(409, "SLUG_VERSION_ALREADY_EXISTS", "Slug+version already exists") from exc
            raise api_error(400, "INVALID_VERSION", "Version must be MAJOR.MINOR.PATCH") from exc

    @app.post("/v1/personas:import", response_model=BulkImportResponse)
    def import_personas(request: Request, payload: BulkImportRequest, created_by: str = Query(default="system")) -> BulkImportResponse:
        store = get_store(request)
        results: list[BulkImportItemResult] = []
        created = 0
        failed = 0
        skipped = 0
        for item in payload.personas:
            try:
                store.create(item, created_by=created_by)
                results.append(BulkImportItemResult(id=item.id, created=True))
                created += 1
            except ValueError as exc:
                error = str(exc)
                if error in {"ID_ALREADY_EXISTS", "SLUG_VERSION_ALREADY_EXISTS"}:
                    skipped += 1
                else:
                    failed += 1
                results.append(BulkImportItemResult(id=item.id, created=False, error=error))
        return BulkImportResponse(created=created, failed=failed, skipped=skipped, results=results)

    @app.get("/v1/personas", response_model=PersonasListResponse)
    def list_personas(
        request: Request,
        slug: str | None = None,
        status: PersonaStatus | None = None,
        tag: str | None = None,
        ai_attitude: str | None = None,
        knowledge_level: str | None = None,
        q: str | None = None,
        limit: int = Query(default=50, ge=1, le=200),
        cursor: int = Query(default=0, ge=0),
    ) -> PersonasListResponse:
        items = get_store(request).list(
            slug=slug,
            status=status,
            tag=tag,
            ai_attitude=ai_attitude,
            knowledge_level=knowledge_level,
            q=q,
        )
        paged = items[cursor : cursor + limit]
        next_cursor = cursor + limit if cursor + limit < len(items) else None
        return PersonasListResponse(items=paged, next_cursor=str(next_cursor) if next_cursor is not None else None, count=len(paged))

    @app.get("/v1/personas/{persona_id}", response_model=PersonaRecord)
    def get_persona_by_id(request: Request, persona_id: str) -> PersonaRecord:
        record = get_store(request).get_by_id(persona_id)
        if not record:
            raise api_error(404, "NOT_FOUND", "Persona not found")
        return record

    @app.get("/v1/personas/{slug}/versions", response_model=list[PersonaRecord])
    def list_persona_versions(request: Request, slug: str) -> list[PersonaRecord]:
        versions = get_store(request).get_versions(slug)
        if not versions:
            raise api_error(404, "NOT_FOUND", "Persona slug not found")
        return versions

    @app.get("/v1/personas/{slug}/versions/{version}", response_model=PersonaRecord)
    def get_persona_version(request: Request, slug: str, version: str) -> PersonaRecord:
        record = get_store(request).get_by_slug_version(slug, version)
        if not record:
            raise api_error(404, "NOT_FOUND", "Persona version not found")
        return record

    @app.get("/v1/personas/{slug}/latest", response_model=PersonaRecord)
    def get_latest_persona(request: Request, slug: str) -> PersonaRecord:
        record = get_store(request).get_latest(slug)
        if not record:
            raise api_error(404, "NOT_FOUND", "No non-draft version found for slug")
        return record

    @app.patch("/v1/personas/{persona_id}", response_model=PersonaRecord)
    def update_persona(request: Request, persona_id: str, update: PersonaUpdate) -> PersonaRecord:
        try:
            return get_store(request).update_draft(persona_id, update)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Persona not found") from exc
        except ValueError as exc:
            raise api_error(400, "ONLY_DRAFT_EDITABLE", "Only draft personas can be edited") from exc

    @app.delete("/v1/personas/{persona_id}")
    def delete_persona(request: Request, persona_id: str) -> dict[str, bool]:
        try:
            get_store(request).delete_draft(persona_id)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Persona not found") from exc
        except ValueError as exc:
            raise api_error(400, "ONLY_DRAFT_DELETABLE", "Only draft personas can be deleted") from exc
        return {"deleted": True}

    @app.post("/v1/personas/{persona_id}:publish", response_model=PersonaRecord)
    def publish_persona(request: Request, persona_id: str, _: TransitionRequest) -> PersonaRecord:
        try:
            return get_store(request).transition(persona_id, PersonaStatus.active)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Persona not found") from exc
        except ValueError as exc:
            raise api_error(400, "INVALID_STATUS_TRANSITION", "Cannot publish from current state") from exc

    @app.post("/v1/personas/{persona_id}:deprecate", response_model=PersonaRecord)
    def deprecate_persona(request: Request, persona_id: str, _: TransitionRequest) -> PersonaRecord:
        try:
            return get_store(request).transition(persona_id, PersonaStatus.deprecated)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Persona not found") from exc
        except ValueError as exc:
            raise api_error(400, "INVALID_STATUS_TRANSITION", "Cannot deprecate from current state") from exc

    @app.post("/v1/personas/{persona_id}:archive", response_model=PersonaRecord)
    def archive_persona(request: Request, persona_id: str, _: TransitionRequest) -> PersonaRecord:
        try:
            return get_store(request).transition(persona_id, PersonaStatus.archived)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Persona not found") from exc
        except ValueError as exc:
            raise api_error(400, "INVALID_STATUS_TRANSITION", "Cannot archive from current state") from exc

    @app.post("/v1/rosters", response_model=RosterRecord)
    def create_roster(request: Request, roster: RosterCreate, created_by: str = Query(default="system")) -> RosterRecord:
        try:
            return get_store(request).create_roster(roster, created_by=created_by)
        except ValueError as exc:
            raise api_error(409, "ROSTER_ID_ALREADY_EXISTS", "Roster ID already exists") from exc

    @app.get("/v1/rosters", response_model=list[RosterRecord])
    def list_rosters(request: Request) -> list[RosterRecord]:
        return get_store(request).list_rosters()

    @app.get("/v1/rosters/{roster_id}", response_model=RosterRecord)
    def get_roster(request: Request, roster_id: str) -> RosterRecord:
        roster = get_store(request).get_roster(roster_id)
        if not roster:
            raise api_error(404, "NOT_FOUND", "Roster not found")
        return roster

    @app.patch("/v1/rosters/{roster_id}", response_model=RosterRecord)
    def update_roster(request: Request, roster_id: str, update: RosterUpdate) -> RosterRecord:
        try:
            return get_store(request).update_roster(roster_id, update)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Roster not found") from exc

    @app.delete("/v1/rosters/{roster_id}")
    def delete_roster(request: Request, roster_id: str) -> dict[str, bool]:
        try:
            get_store(request).delete_roster(roster_id)
        except KeyError as exc:
            raise api_error(404, "NOT_FOUND", "Roster not found") from exc
        return {"deleted": True}

    @app.post("/v1/evaluations", response_model=EvaluationRecord)
    def create_evaluation(request: Request, payload: EvaluationCreateRequest) -> EvaluationRecord:
        try:
            return get_store(request).create_evaluation(payload)
        except ValueError as exc:
            code = str(exc)
            if code == "TARGET_NOT_FOUND":
                raise api_error(404, "TARGET_NOT_FOUND", "Evaluation target not found") from exc
            raise api_error(400, "INVALID_TARGET", "Invalid evaluation target") from exc

    @app.get("/v1/evaluations/{evaluation_id}", response_model=EvaluationRecord)
    def get_evaluation(request: Request, evaluation_id: str) -> EvaluationRecord:
        evaluation = get_store(request).get_evaluation(evaluation_id)
        if not evaluation:
            raise api_error(404, "NOT_FOUND", "Evaluation not found")
        return evaluation

    @app.get("/v1/evaluations/{evaluation_id}/results", response_model=EvaluationRecord)
    def get_evaluation_results(request: Request, evaluation_id: str) -> EvaluationRecord:
        evaluation = get_store(request).get_evaluation(evaluation_id)
        if not evaluation:
            raise api_error(404, "NOT_FOUND", "Evaluation results not found")
        return evaluation

    @app.post("/v1/evaluations:compare", response_model=EvaluationCompareResponse)
    def compare_evaluations(request: Request, payload: EvaluationCompareRequest) -> EvaluationCompareResponse:
        items = get_store(request).compare_evaluations(payload.evaluation_ids)
        return EvaluationCompareResponse(items=items)

    return app


app = create_app()
