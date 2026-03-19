from fastapi.testclient import TestClient
from pathlib import Path
from uuid import uuid4

from app.main import create_app


def persona_payload(persona_id: str, slug: str, version: str) -> dict:
    return {
        "id": persona_id,
        "slug": slug,
        "name": "Arnold",
        "version": version,
        "summary": "Experienced business stakeholder who is skeptical of AI hype.",
        "knowledge_level": "medium",
        "ai_attitude": "skeptical",
        "traits": ["practical", "risk-aware"],
        "communication_style": ["direct", "low-jargon"],
        "goals": ["Understand real business value"],
        "frustrations": ["Buzzwords"],
        "prompt_template": "Respond as Arnold...",
        "usage_guidance": {
            "best_for": ["executive reviews"],
            "avoid_for": ["open brainstorming"],
        },
        "tags": ["skeptic", "business"],
        "status": "draft",
    }


def make_client(database_path: Path) -> TestClient:
    database_url = f"sqlite:///{database_path.as_posix()}"
    return TestClient(create_app(database_url=database_url))


def test_create_and_get_persona(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_create_and_get_persona.db")
    suffix = uuid4().hex[:6]
    persona_id = f"persona_arnold_v3_{suffix}"
    slug = f"arnold-ai-skeptic-{suffix}"
    payload = persona_payload(persona_id, slug, "3.0.0")
    create_response = client.post("/v1/personas", json=payload)
    assert create_response.status_code == 200
    body = create_response.json()
    assert body["id"] == persona_id

    get_response = client.get(f"/v1/personas/{persona_id}")
    assert get_response.status_code == 200
    assert get_response.json()["slug"] == slug


def test_invalid_transition_draft_to_archive(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_invalid_transition_draft_to_archive.db")
    suffix = uuid4().hex[:6]
    persona_id = f"persona_transition_test_{suffix}"
    payload = persona_payload(persona_id, f"transition-test-{suffix}", "1.0.0")
    client.post("/v1/personas", json=payload)

    archive_response = client.post(f"/v1/personas/{persona_id}:archive", json={"actor": "qa"})
    assert archive_response.status_code == 400
    assert archive_response.json()["detail"]["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_latest_ignores_draft(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_latest_ignores_draft.db")
    suffix = uuid4().hex[:6]
    slug = f"latest-check-{suffix}"
    v1 = persona_payload(f"persona_latest_v1_{suffix}", slug, "1.0.0")
    v2 = persona_payload(f"persona_latest_v2_{suffix}", slug, "1.1.0")
    client.post("/v1/personas", json=v1)
    client.post("/v1/personas", json=v2)

    publish_response = client.post(f"/v1/personas/{v1['id']}:publish", json={"actor": "qa"})
    assert publish_response.status_code == 200

    latest_response = client.get(f"/v1/personas/{slug}/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == v1["id"]


def test_delete_draft_persona(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_delete_draft_persona.db")
    suffix = uuid4().hex[:6]
    persona_id = f"persona_delete_draft_{suffix}"
    payload = persona_payload(persona_id, f"delete-draft-{suffix}", "1.0.0")

    create_response = client.post("/v1/personas", json=payload)
    assert create_response.status_code == 200

    delete_response = client.delete(f"/v1/personas/{persona_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    get_response = client.get(f"/v1/personas/{persona_id}")
    assert get_response.status_code == 404


def test_delete_non_draft_persona_rejected(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_delete_non_draft_persona_rejected.db")
    suffix = uuid4().hex[:6]
    persona_id = f"persona_delete_active_{suffix}"
    payload = persona_payload(persona_id, f"delete-active-{suffix}", "1.0.0")

    create_response = client.post("/v1/personas", json=payload)
    assert create_response.status_code == 200
    publish_response = client.post(f"/v1/personas/{persona_id}:publish", json={"actor": "qa"})
    assert publish_response.status_code == 200

    delete_response = client.delete(f"/v1/personas/{persona_id}")
    assert delete_response.status_code == 400
    assert delete_response.json()["detail"]["error"]["code"] == "ONLY_DRAFT_DELETABLE"


def test_roster_crud(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_roster_crud.db")
    suffix = uuid4().hex[:6]
    payload = {
        "id": f"roster_{suffix}",
        "name": "Exec Risk Roster",
        "items": [
            {
                "slug": "arnold-ai-skeptic",
                "version_selector": "latest",
                "role": "primary_reviewer",
                "business_function": "compliance",
                "task_type": "risk-review",
            }
        ],
        "tags": ["exec", "risk"],
    }

    create_response = client.post("/v1/rosters", json=payload)
    assert create_response.status_code == 200

    get_response = client.get(f"/v1/rosters/{payload['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Exec Risk Roster"

    patch_response = client.patch(f"/v1/rosters/{payload['id']}", json={"name": "Updated Roster"})
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Updated Roster"

    delete_response = client.delete(f"/v1/rosters/{payload['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_evaluation_and_compare(tmp_path: Path) -> None:
    client = make_client(tmp_path / "test_evaluation_and_compare.db")
    suffix = uuid4().hex[:6]
    persona = persona_payload(f"persona_eval_{suffix}", f"eval-slug-{suffix}", "1.0.0")
    client.post("/v1/personas", json=persona)
    client.post(f"/v1/personas/{persona['id']}:publish", json={"actor": "qa"})

    eval_request = {
        "target": {"type": "persona", "slug": persona["slug"], "version_selector": "latest"},
        "input": {"task": "Review this proposal", "context": "context"},
        "options": {"record_transcript": True, "max_tokens": 500, "scoring_mode": "hybrid_weighted", "weights": {"automated": 0.6, "human": 0.4}},
    }

    eval_response = client.post("/v1/evaluations", json=eval_request)
    assert eval_response.status_code == 200
    evaluation_id = eval_response.json()["id"]

    compare_response = client.post("/v1/evaluations:compare", json={"evaluation_ids": [evaluation_id]})
    assert compare_response.status_code == 200
    assert len(compare_response.json()["items"]) == 1


def test_persistence_survives_new_app_instance(tmp_path: Path) -> None:
    suffix = uuid4().hex[:6]
    database_path = tmp_path / f"test_persistence_{suffix}.db"
    persona_id = f"persona_persist_{suffix}"
    slug = f"persist-slug-{suffix}"

    with make_client(database_path) as first_client:
        create_response = first_client.post("/v1/personas", json=persona_payload(persona_id, slug, "1.0.0"))
        assert create_response.status_code == 200

    with make_client(database_path) as second_client:
        get_response = second_client.get(f"/v1/personas/{persona_id}")
        assert get_response.status_code == 200
        assert get_response.json()["slug"] == slug
