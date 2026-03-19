from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401

DEFAULT_DB_URL = "sqlite:///./data/persona_registry.db"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_database_url(url: str) -> str:
    if not url.startswith("sqlite:///"):
        return url
    parsed = urlparse(url)
    raw_path = parsed.path.lstrip("/")
    database_path = Path(raw_path)
    if not database_path.is_absolute():
        database_path = project_root() / database_path
    database_path = database_path.resolve()
    return f"sqlite:///{database_path.as_posix()}"


def resolve_database_url(database_url: str | None = None) -> str:
    configured_url = database_url or os.getenv("PERSONA_REGISTRY_DB_URL", DEFAULT_DB_URL)
    return normalize_database_url(configured_url)


def create_session_factory(database_url: str | None = None) -> tuple[str, Callable[[], Session]]:
    resolved_url = resolve_database_url(database_url)
    if resolved_url.startswith("sqlite:///"):
        parsed = urlparse(resolved_url)
        database_path = Path(parsed.path.lstrip("/"))
        database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(resolved_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def session_factory() -> Session:
        return Session(engine)

    return resolved_url, session_factory