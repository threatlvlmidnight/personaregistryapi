# Persona Registry API — Sprint-Ready Ticket Plan (Jira Style)

Source inputs:
- [v1-implementation-backlog.md](v1-implementation-backlog.md)
- [persona-registry-design-spec.md](persona-registry-design-spec.md)

## Planning Model
- Estimation scale: Fibonacci story points (`1, 2, 3, 5, 8, 13`)
- Team assumption: 1 cross-functional squad
- Target cadence: 2-week sprints
- Critical path theme: resolver correctness + evaluation quality + security baseline

## Epics
- `PR-E1` Persona Registry Core
- `PR-E2` Resolver Correctness & Governance
- `PR-E3` Rosters & Classification
- `PR-E4` Evaluations & Comparison
- `PR-E5` Security, Compliance & Audit Baseline
- `PR-E6` Reliability & Performance SLOs
- `PR-E7` Cost Guardrails
- `PR-E8` Integrations (Ticketing + Docs)

---

## Sprint 1 — Core Registry + Governance Foundations

### PR-101 — Create draft personas API
- **Epic:** `PR-E1`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Implement `POST /v1/personas` with validation and metadata.
- **Acceptance Criteria:**
  - Draft persona persists with required metadata.
  - Validation covers slug/version/required fields.
  - Duplicate ID and duplicate slug+version rejected.
- **Dependencies:** None

### PR-102 — Persona retrieval and search
- **Epic:** `PR-E1`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Implement `GET /v1/personas` and `GET /v1/personas/{id}`.
- **Acceptance Criteria:**
  - Filtering works for status/tag/attitude/knowledge level.
  - Pagination via cursor works.
  - Not-found behavior conforms to error contract.
- **Dependencies:** `PR-101`

### PR-103 — Version listing + latest resolver
- **Epic:** `PR-E1`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Implement `GET /v1/personas/{slug}/versions` and `/latest` with deterministic semver resolution.
- **Acceptance Criteria:**
  - Semver sorting is deterministic.
  - Latest excludes draft.
  - Edge cases with deprecated/archived are explicitly handled.
- **Dependencies:** `PR-101`

### PR-104 — Lifecycle transitions API
- **Epic:** `PR-E1`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Implement publish/deprecate/archive transition endpoints.
- **Acceptance Criteria:**
  - Only valid transitions succeed.
  - Deprecated remains callable until archived.
  - Invalid transitions return structured error codes.
- **Dependencies:** `PR-101`, `PR-103`

### PR-105 — Single-owner publish authorization
- **Epic:** `PR-E2`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Add single-owner checks to publish/deprecate/archive paths.
- **Acceptance Criteria:**
  - Non-owner transitions are denied.
  - Owner mapping is configurable.
  - Auth failures are audited.
- **Dependencies:** `PR-104`

### PR-106 — Resolver contract test suite
- **Epic:** `PR-E2`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Add contract tests for `id`, `slug+version`, and `slug+latest` resolution.
- **Acceptance Criteria:**
  - Tests include archived/deprecated behavior.
  - Any resolver mismatch fails CI.
- **Dependencies:** `PR-103`, `PR-104`

**Sprint 1 Target SP:** `36`

---

## Sprint 2 — Rosters + Evaluations + Comparison

### PR-201 — Persona import endpoint
- **Epic:** `PR-E1`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Implement `POST /v1/personas:import` with per-item result reporting.
- **Acceptance Criteria:**
  - Bulk payload supports partial success.
  - Import report includes created/skipped/failed counts.
- **Dependencies:** `PR-101`

### PR-202 — Roster CRUD endpoints
- **Epic:** `PR-E3`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Implement `POST/GET/PATCH/DELETE /v1/rosters`.
- **Acceptance Criteria:**
  - Roster item references support exact version and `latest`.
  - Duplicate equivalent entries are rejected.
- **Dependencies:** `PR-103`

### PR-203 — Hybrid roster classification
- **Epic:** `PR-E3`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Support `business_function` and `task_type` with filtering.
- **Acceptance Criteria:**
  - Classification fields persist and filter correctly.
  - Vocabulary validation behavior defined and tested.
- **Dependencies:** `PR-202`

### PR-204 — Evaluation run API
- **Epic:** `PR-E4`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Implement `POST /v1/evaluations` + status/results endpoints.
- **Acceptance Criteria:**
  - Supports persona and roster targets.
  - Transcript recording follows policy.
  - Results are normalized and queryable.
- **Dependencies:** `PR-202`

### PR-205 — Hybrid weighted scoring
- **Epic:** `PR-E4`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Add automated + human weighted score model.
- **Acceptance Criteria:**
  - Default weight profile supported.
  - Score components and aggregate persisted.
  - Rubric version included in result.
- **Dependencies:** `PR-204`

### PR-206 — Evaluation compare endpoint
- **Epic:** `PR-E4`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Implement `POST /v1/evaluations:compare`.
- **Acceptance Criteria:**
  - Supports persona-vs-persona and roster comparisons.
  - Payload includes score deltas and transcript links.
- **Dependencies:** `PR-204`, `PR-205`

**Sprint 2 Target SP:** `39`

---

## Sprint 3 — Security + Reliability + Integrations + Cost Controls

### PR-301 — PII controls and redaction policy
- **Epic:** `PR-E5`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Implement redaction/minimization for stored context/transcripts.
- **Acceptance Criteria:**
  - Redaction policy configurable by environment.
  - Sensitive storage behavior documented and tested.
- **Dependencies:** `PR-204`

### PR-302 — Audit retention + role access baseline
- **Epic:** `PR-E5`
- **Story Points:** `8`
- **Priority:** `P0`
- **Description:** Enforce retention policy and role checks across protected endpoints.
- **Acceptance Criteria:**
  - Audit logs for all lifecycle/evaluation actions.
  - Retention policy configurable and verified.
- **Dependencies:** `PR-104`, `PR-204`

### PR-303 — Latency SLO instrumentation
- **Epic:** `PR-E6`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Add P50/P95/P99 metrics and alert thresholds for evaluation endpoints.
- **Acceptance Criteria:**
  - Dashboards and alerts configured.
  - SLO breaches visible and actionable.
- **Dependencies:** `PR-204`

### PR-304 — Request tracing + structured errors
- **Epic:** `PR-E6`
- **Story Points:** `5`
- **Priority:** `P0`
- **Description:** Ensure request IDs and structured error observability across APIs.
- **Acceptance Criteria:**
  - Request IDs propagated in logs and responses.
  - Error classes visible by rate and endpoint.
- **Dependencies:** `PR-101`, `PR-204`

### PR-305 — Cost guardrails enforcement
- **Epic:** `PR-E7`
- **Story Points:** `8`
- **Priority:** `P1`
- **Description:** Enforce per-run cap, monthly soft cap, and model allowlist.
- **Acceptance Criteria:**
  - Budget policy blocks/flags as configured.
  - Allowlist enforcement with audited overrides.
- **Dependencies:** `PR-204`

### PR-306 — Ticketing events integration
- **Epic:** `PR-E8`
- **Story Points:** `5`
- **Priority:** `P1`
- **Description:** Implement `POST /v1/integrations/tickets/events`.
- **Acceptance Criteria:**
  - Event schema includes actor/action/target/status.
  - Delivery failures retry with dead-letter logging.
- **Dependencies:** `PR-104`, `PR-204`

### PR-307 — Docs publishing integration
- **Epic:** `PR-E8`
- **Story Points:** `5`
- **Priority:** `P1`
- **Description:** Implement `POST /v1/integrations/docs/publish`.
- **Acceptance Criteria:**
  - Persona/evaluation summaries publish in template format.
  - Publish history and retries are supported.
- **Dependencies:** `PR-204`

**Sprint 3 Target SP:** `44`

---

## Release Gate Checklist (V1)
- Resolver correctness tests are green (`PR-106`).
- Lifecycle transition guards are enforced (`PR-104`, `PR-105`).
- Evaluation + compare workflows are production ready (`PR-204` to `PR-206`).
- Security baseline complete (`PR-301`, `PR-302`).
- Reliability SLO instrumentation active (`PR-303`, `PR-304`).

## If Capacity Tightens (Deferral Order)
1. `PR-307` docs publishing integration
2. `PR-306` ticketing integration
3. `PR-305` advanced override UX (keep core guardrails)
4. Non-critical taxonomy enhancements in roster vocabulary tooling

## Suggested Jira Labels
- `area:registry`
- `area:resolver`
- `area:evaluation`
- `area:security`
- `area:observability`
- `area:integration`
- `priority:p0`
- `priority:p1`
- `release:v1`
