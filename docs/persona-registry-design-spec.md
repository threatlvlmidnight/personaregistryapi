# Persona Registry API — Design Spec (Draft v0.1)

## 1) Purpose
Build a versioned Persona Registry API so tools (including Copilot sessions) can:
- retrieve stable persona definitions,
- evaluate prompts/responses against specific personas,
- manage persona rosters for repeatable testing and task-specific simulation.

## 2) Problem Statement
Prompt behavior changes depending on persona framing, but teams often lack:
- a central registry for canonical persona definitions,
- version control for persona evolution,
- repeatable evaluation workflows tied to persona versions,
- shareable persona rosters for different testing scenarios.

## 3) Goals
- Primary outcome: improve response quality for persona-driven testing.
- Provide CRUD + search for personas with semantic versioning.
- Support immutable published versions and draft editing flow.
- Enable resolution by ID, slug, and "latest" selectors.
- Support roster creation with hybrid classification (business function + task type).
- Support evaluation workflows that compare results across personas/rosters.
- Keep API simple and tool-friendly for technical first users (prompt engineer, developer, QA lead).

## 4) Non-Goals (V1)
- Full orchestration of LLM providers.
- Persona auto-generation from documents.
- Fine-grained collaboration workflows (comments/approvals).
- Real-time streaming protocol design.

## 5) Core Domain Model

### 5.1 PersonaVersion (primary resource)
```json
{
  "id": "persona_arnold_v3",
  "slug": "arnold-ai-skeptic",
  "name": "Arnold",
  "version": "3.0.0",
  "summary": "Experienced business stakeholder who is skeptical of AI hype.",
  "knowledge_level": "medium",
  "ai_attitude": "skeptical",
  "traits": ["practical", "risk-aware", "demands evidence"],
  "communication_style": ["direct", "low-jargon", "results-focused"],
  "goals": [
    "Understand real business value",
    "Avoid unnecessary complexity",
    "See measurable ROI"
  ],
  "frustrations": [
    "Buzzwords",
    "Overpromising",
    "Vague answers"
  ],
  "prompt_template": "Respond as Arnold, an AI skeptic who values evidence, clarity, and ROI...",
  "usage_guidance": {
    "best_for": ["executive reviews", "risk analysis", "vendor evaluation"],
    "avoid_for": ["creative brainstorming without constraints"]
  },
  "tags": ["skeptic", "business", "stakeholder"],
  "status": "active"
}
```

### 5.2 Required metadata (V1 additions)
- `created_at` (ISO timestamp)
- `updated_at` (ISO timestamp)
- `created_by` (actor/service ID)
- `changelog` (string, required for non-initial versions)
- `source_version` (e.g. `2.1.0`, nullable for first release)
- `is_latest` (derived, read-only)

### 5.3 Enumerations (initial)
- `knowledge_level`: `low | medium | high`
- `ai_attitude`: `skeptical | neutral | optimistic`
- `status`: `draft | active | deprecated | archived`

## 6) Versioning Strategy
- Use semantic versioning (`MAJOR.MINOR.PATCH`) per persona slug.
- `slug` identifies persona family, `version` identifies immutable snapshot.
- Only one `draft` version per `slug` at a time.
- `active` versions are immutable (Q6 policy is currently pending final confirmation).
- `latest` resolution returns highest non-draft version by semver.

### 6.1 Allowed transitions
- `draft -> active`
- `active -> deprecated`
- `deprecated -> archived`
- Deprecated versions remain callable until explicitly archived (no auto-archive in v1).
- No reverse transitions in V1.

## 7) API Surface (REST, `/v1`)

### 7.1 Personas
- `POST /v1/personas`
  - Create new draft persona version.
- `POST /v1/personas:import`
  - Import one or more persona definitions for onboarding/migration workflows.
- `GET /v1/personas`
  - List/search personas.
  - Query params: `slug`, `name`, `status`, `tag`, `ai_attitude`, `knowledge_level`, `q`, `limit`, `cursor`.
- `GET /v1/personas/{id}`
  - Fetch by unique ID.
- `GET /v1/personas/{slug}/versions`
  - List versions for a persona family.
- `GET /v1/personas/{slug}/versions/{version}`
  - Fetch specific version.
- `GET /v1/personas/{slug}/latest`
  - Fetch latest non-draft version.
- `PATCH /v1/personas/{id}`
  - Update draft version fields.
- `POST /v1/personas/{id}:publish`
  - Publish draft to `active`; version must be valid semver.
- `POST /v1/personas/{id}:deprecate`
  - Move active -> deprecated with reason.
- `POST /v1/personas/{id}:archive`
  - Move deprecated -> archived.

### 7.2 Rosters
Roster = named set of persona references for repeatable tests.
- `POST /v1/rosters`
- `GET /v1/rosters`
- `GET /v1/rosters/{roster_id}`
- `PATCH /v1/rosters/{roster_id}`
- `DELETE /v1/rosters/{roster_id}`

Roster item shape:
```json
{
  "slug": "arnold-ai-skeptic",
  "version_selector": "3.0.0",
  "role": "primary_reviewer",
  "business_function": "compliance",
  "task_type": "risk-review"
}
```
`version_selector` supports exact version or `latest`.

### 7.3 Evaluations
Runs a prompt/task against one persona version or an entire roster.
- `POST /v1/evaluations`
- `GET /v1/evaluations/{evaluation_id}`
- `GET /v1/evaluations/{evaluation_id}/results`
- `POST /v1/evaluations:compare`
  - Compare outcomes across persona targets or roster runs.

Create evaluation request:
```json
{
  "target": {
    "type": "roster",
    "roster_id": "roster_exec_risk_v1"
  },
  "input": {
    "task": "Review this AI proposal for business risk and ROI realism",
    "context": "...optional context..."
  },
  "options": {
    "record_transcript": true,
    "max_tokens": 1200,
    "scoring_mode": "hybrid_weighted",
    "weights": {
      "automated": 0.6,
      "human": 0.4
    }
  }
}
```

### 7.4 Integration Endpoints (V1)
- `POST /v1/integrations/tickets/events`
  - Emit evaluation/persona lifecycle events to ticketing systems.
- `POST /v1/integrations/docs/publish`
  - Publish persona and evaluation summaries to documentation/wiki targets.

## 8) Response & Error Conventions
- JSON only.
- Use envelope for list endpoints:
```json
{
  "items": [],
  "next_cursor": "...",
  "count": 0
}
```
- Error format:
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "Cannot archive an active persona",
    "details": {}
  }
}
```

## 9) Validation Rules (V1)
- `id`: unique, immutable.
- `slug`: lowercase kebab-case, immutable across versions.
- `version`: valid semver.
- `prompt_template`: non-empty, max length TBD.
- Array fields (`traits`, `goals`, etc.) de-duplicated and trimmed.
- `status=active` requires all required fields present.
- Publish approval model is single owner in v1.

## 10) Storage Model (logical)

### 10.1 Tables/collections
- `persona_versions`
- `rosters`
- `roster_items`
- `evaluations`
- `evaluation_results`

### 10.3 Deployment/Tenancy
- v1 is single-tenant by design.
- Tenant isolation abstractions are out of scope for v1 and planned for future phases.

### 10.2 Uniqueness
- `(slug, version)` unique.
- `id` unique.
- Optional index on tags + status for search.

## 11) Auth, Access, and Audit
- Auth: API key or OAuth token (implementation choice).
- Roles (V1): `reader`, `editor`, `admin`.
- Audit log required for create/update/publish/deprecate/archive actions.
- Evaluation requests should record actor and timestamp.
- Access controls must enforce team-scoped permissions for persona and evaluation operations.
- Audit retention policy is required as part of security baseline.
- PII handling controls (redaction/minimization) are required for stored transcripts and context.

## 12) Observability
- Request ID in headers and logs.
- Basic metrics:
  - persona reads/writes,
  - publish/deprecate counts,
  - evaluation success/error/latency,
  - top persona slugs used,
  - stakeholder adoption indicators,
  - reusable persona count,
  - deprecated-version usage.

### 12.1 Reliability Targets
- Resolver correctness is a critical quality gate (wrong persona/version resolution is unacceptable).
- Evaluation latency SLOs are required for user-facing workflows.

## 13) Open Questions
- Should `latest` include `deprecated` or only `active`?
- Should evaluations be synchronous for small payloads and async for large?
- Do we need persona compatibility constraints by model/provider?
- Which fields (if any) remain mutable after publish? (pending final Q6 decision)

## 14) Suggested V1 Milestones
1. Persona CRUD + import + version retrieval.
2. Publish/deprecate/archive workflow + single-owner approval.
3. Roster CRUD with hybrid classification fields.
4. Evaluation create/status/results + compare + hybrid weighted scoring.
5. Security baseline (PII controls, audit retention, access control) + metrics hardening.
6. Initial integrations: ticketing events and docs publishing.

## 15) Cost Guardrails (V1)
- Enforce per-run budget caps for evaluations.
- Enforce monthly soft spend caps.
- Enforce model-tier allowlist for evaluation execution.
- Support authorized override events with audit logging.

---

## Appendix A: Minimal Persona JSON Schema (draft)
```json
{
  "type": "object",
  "required": [
    "id", "slug", "name", "version", "summary",
    "knowledge_level", "ai_attitude", "traits",
    "communication_style", "goals", "frustrations",
    "prompt_template", "tags", "status"
  ],
  "properties": {
    "id": { "type": "string", "minLength": 3 },
    "slug": { "type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "knowledge_level": { "enum": ["low", "medium", "high"] },
    "ai_attitude": { "enum": ["skeptical", "neutral", "optimistic"] },
    "status": { "enum": ["draft", "active", "deprecated", "archived"] }
  }
}
```