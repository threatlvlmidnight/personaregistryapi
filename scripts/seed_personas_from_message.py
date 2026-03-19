from __future__ import annotations

import argparse
import re
from pathlib import Path

from app.db import create_session_factory
from app.schemas import AIAttitude, KnowledgeLevel, PersonaCreate, PersonaStatus
from app.store import PersonaStore


def parse_persona_blocks(source: str) -> list[dict[str, str]]:
    block_pattern = re.compile(
        r"'(?P<key>[a-z0-9-]+)'\s*:\s*\{(?P<body>.*?)\n\s*\},",
        re.DOTALL,
    )
    field_pattern = re.compile(r"(?P<field>id|name|emoji|role|description|table|model)\s*:\s*'(?P<value>[^']*)'")
    prompt_pattern = re.compile(r"systemPrompt\s*:\s*`(?P<value>.*?)`", re.DOTALL)

    personas: list[dict[str, str]] = []
    for match in block_pattern.finditer(source):
        body = match.group("body")
        fields: dict[str, str] = {"key": match.group("key")}
        for field_match in field_pattern.finditer(body):
            fields[field_match.group("field")] = field_match.group("value").strip()
        prompt_match = prompt_pattern.search(body)
        if prompt_match:
            fields["systemPrompt"] = " ".join(prompt_match.group("value").split())

        required = {"id", "name", "role", "description", "table", "model", "systemPrompt"}
        if required.issubset(fields):
            personas.append(fields)
    return personas


def infer_knowledge_level(table: str) -> KnowledgeLevel:
    mapping = {
        "security": KnowledgeLevel.high,
        "engineering": KnowledgeLevel.high,
        "business": KnowledgeLevel.medium,
        "ops": KnowledgeLevel.medium,
        "product": KnowledgeLevel.medium,
        "fresh-eyes": KnowledgeLevel.low,
    }
    return mapping.get(table, KnowledgeLevel.medium)


def infer_ai_attitude(persona_id: str, role: str, description: str) -> AIAttitude:
    lowered = f"{persona_id} {role} {description}".lower()
    if any(token in lowered for token in ["skeptic", "pessimist", "security", "hacker", "oncall", "compliance"]):
        return AIAttitude.skeptical
    if "optimist" in lowered:
        return AIAttitude.optimistic
    return AIAttitude.neutral


def list_from_description(description: str) -> list[str]:
    parts = [item.strip().lower() for item in re.split(r",| and ", description) if item.strip()]
    unique: list[str] = []
    seen: set[str] = set()
    for part in parts:
        normalized = part.replace(" ", "-")
        if normalized not in seen:
            unique.append(normalized)
            seen.add(normalized)
    return unique[:4]


def build_persona_payload(item: dict[str, str]) -> PersonaCreate:
    table = item["table"]
    description = item["description"]
    role = item["role"]
    return PersonaCreate(
        id=item["id"],
        slug=item["id"],
        name=item["name"],
        version="1.0.0",
        summary=description,
        knowledge_level=infer_knowledge_level(table),
        ai_attitude=infer_ai_attitude(item["id"], role, description),
        traits=list_from_description(description) or ["pragmatic"],
        communication_style=["direct", "concise"],
        goals=[f"Improve {table} outcomes", f"Represent {role.lower()} perspective"],
        frustrations=["vague requirements", "avoidable risk"],
        prompt_template=item["systemPrompt"],
        usage_guidance={
            "best_for": [table, role.lower()],
            "avoid_for": ["generic brainstorming without context"],
        },
        tags=[table, item["model"], role.lower().replace(" ", "-")],
        status=PersonaStatus.active,
    )


def seed(input_file: Path, database_url: str | None = None) -> tuple[int, int]:
    text = input_file.read_text(encoding="utf-8")
    parsed = parse_persona_blocks(text)
    _, session_factory = create_session_factory(database_url)
    store = PersonaStore(session_factory)

    created = 0
    skipped = 0
    for item in parsed:
        payload = build_persona_payload(item)
        try:
            store.create(payload, created_by="seed-script")
            created += 1
        except ValueError as exc:
            if str(exc) in {"ID_ALREADY_EXISTS", "SLUG_VERSION_ALREADY_EXISTS"}:
                skipped += 1
            else:
                raise
    return created, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed personas from message.txt into the SQLite DB")
    parser.add_argument("--input", default="message.txt", help="Path to message.txt containing ALL_PERSONAS")
    parser.add_argument("--database-url", default=None, help="Optional database URL override")
    args = parser.parse_args()

    created, skipped = seed(Path(args.input), args.database_url)
    print(f"Seed complete: created={created}, skipped={skipped}")


if __name__ == "__main__":
    main()