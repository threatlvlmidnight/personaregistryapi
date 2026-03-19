from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


class PersonaModel(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("slug", "version", name="uq_persona_slug_version"),)

    id: str = Field(primary_key=True)
    slug: str = Field(index=True)
    name: str
    version: str = Field(index=True)
    summary: str
    knowledge_level: str
    ai_attitude: str
    traits: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    communication_style: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    goals: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    frustrations: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    prompt_template: str
    usage_guidance: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    status: str = Field(index=True)
    changelog: str | None = None
    source_version: str | None = None
    created_at: str
    updated_at: str
    created_by: str
    is_latest: bool = False


class RosterModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    items: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    created_at: str
    updated_at: str
    created_by: str


class EvaluationModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    status: str
    target: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    input: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    options: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    score_automated: float
    score_human: float
    score_total: float
    created_at: str
    updated_at: str