# Persona Registry API — V1 Implementation Backlog

Derived from:
- [persona-registry-design-spec.md](persona-registry-design-spec.md)
- [design-decision-template.md](design-decision-template.md)

## Planning Assumptions
- Deployment model is single-tenant for v1.
- Primary product objective is improved response quality.
- First users are prompt engineer, developer, and QA lead.
- Critical failures to prevent: wrong persona/version resolution and high evaluation latency.

## Priority Model
- P0 = must ship for viable v1
- P1 = strongly recommended for v1
- P2 = can move to v1.1 if schedule pressure

---

## Epic E1 — Persona Registry Core (P0)

### Story E1-S1 — Create and store persona drafts
**As a** developer, **I want** to create draft personas, **so that** I can iterate before publish.

**Acceptance Criteria**
- `POST /v1/personas` stores a draft with required fields and metadata.
- Validation rejects invalid `slug`, invalid `version`, and missing required fields.
- Response includes server-generated metadata (`created_at`, `updated_at`, `created_by`).
- Duplicate `id` and duplicate `(slug, version)` are rejected with clear error codes.

### Story E1-S2 — Import personas in bulk
**As a** prompt engineer, **I want** bulk import, **so that** I can bootstrap the registry quickly.

**Acceptance Criteria**
- `POST /v1/personas:import` accepts one or more persona payloads.
- Supports partial success with per-item result details.
- Import report returns counts for created, skipped, failed.
- Validation errors are item-specific and actionable.

### Story E1-S3 — Retrieve personas and versions
**As a** QA lead, **I want** stable retrieval and search, **so that** tests are repeatable.

**Acceptance Criteria**
- `GET /v1/personas` supports filtering by status, tags, attitudes, and query string.
- `GET /v1/personas/{id}` returns exact resource or not-found error.
- `GET /v1/personas/{slug}/versions` lists versions sorted by semantic version.
- `GET /v1/personas/{slug}/latest` resolves highest non-draft version deterministically.

### Story E1-S4 — Publish and lifecycle transitions
**As an** owner, **I want** controlled publish and deprecation, **so that** production usage is governed.

**Acceptance Criteria**
- `POST /v1/personas/{id}:publish` transitions `draft -> active` only.
- `POST /v1/personas/{id}:deprecate` transitions `active -> deprecated` only.
- `POST /v1/personas/{id}:archive` transitions `deprecated -> archived` only.
- Deprecated versions remain callable until archived.
- Transition violations return `INVALID_STATUS_TRANSITION` style errors.

---

## Epic E2 — Resolver Correctness and Governance (P0)

### Story E2-S1 — Enforce immutable active versions policy point
**As a** QA lead, **I want** active versions to be stable, **so that** evaluation results are reproducible.

**Acceptance Criteria**
- Editing active versions is blocked by default.
- Draft-only fields remain editable until publish.
- Publish creates immutable snapshot behavior in persistence layer.
- Q6 policy is represented as configuration toggle if final policy changes.

### Story E2-S2 — Single-owner publish authorization
**As an** admin, **I want** clear publish ownership, **so that** governance remains lightweight in v1.

**Acceptance Criteria**
- Publish endpoints require owner-level authorization.
- Non-owner attempts are rejected with authorization error.
- Audit records include actor, action, target, timestamp.
- Owner role mapping is documented and test-covered.

### Story E2-S3 — Resolver contract tests
**As a** developer, **I want** resolver correctness checks, **so that** wrong persona/version resolution does not reach production.

**Acceptance Criteria**
- Contract tests cover `id`, `slug+version`, and `slug+latest` lookup paths.
- Contract tests include archived/deprecated edge cases.
- Deterministic behavior is proven under concurrent publish events.
- Any resolver mismatch fails CI as release blocker.

---

## Epic E3 — Rosters and Classification (P0)

### Story E3-S1 — CRUD rosters
**As a** prompt engineer, **I want** roster management, **so that** I can reuse persona sets across tasks.

**Acceptance Criteria**
- `POST/GET/PATCH/DELETE /v1/rosters` fully functional.
- Roster items reference persona by `slug + version_selector`.
- `version_selector` supports explicit version and `latest`.
- Validation prevents duplicate equivalent roster entries.

### Story E3-S2 — Hybrid roster metadata
**As a** QA lead, **I want** function and task classification, **so that** rosters are discoverable by context.

**Acceptance Criteria**
- `business_function` and `task_type` fields are supported on roster items.
- List endpoints filter by function and task type.
- Controlled vocabulary can be configured and validated.
- Unknown tags return validation warning or error per policy.

---

## Epic E4 — Evaluations and Comparison (P0)

### Story E4-S1 — Run persona or roster evaluations
**As a** developer, **I want** to run evaluations by persona or roster, **so that** I can test behavior systematically.

**Acceptance Criteria**
- `POST /v1/evaluations` accepts persona target and roster target.
- `GET /v1/evaluations/{evaluation_id}` reports lifecycle state.
- `GET /v1/evaluations/{evaluation_id}/results` returns normalized result structure.
- Transcript recording is optional and policy-controlled.

### Story E4-S2 — Hybrid weighted scoring
**As a** prompt engineer, **I want** human + automated scoring, **so that** quality decisions are both scalable and nuanced.

**Acceptance Criteria**
- Supports `scoring_mode=hybrid_weighted` with default weights.
- Automated and human scores are stored separately and as aggregate.
- Rubric version is persisted with each result.
- Weight values are validated and normalized.

### Story E4-S3 — Compare evaluation outcomes
**As a** QA lead, **I want** side-by-side comparisons, **so that** I can choose stronger personas for a task.

**Acceptance Criteria**
- `POST /v1/evaluations:compare` returns multi-target comparison payload.
- Payload includes scores, key deltas, and links to transcripts.
- Comparison works for persona-vs-persona and roster-run comparisons.
- Ordering and tie-breaking logic is deterministic and documented.

---

## Epic E5 — Security, Compliance, and Audit Baseline (P0)

### Story E5-S1 — PII handling controls
**As an** admin, **I want** PII-safe handling, **so that** sensitive data is protected.

**Acceptance Criteria**
- Input/context/transcripts can be redacted or minimized before storage.
- Redaction policy is configurable by environment.
- Storage paths for sensitive artifacts are documented.
- PII policy behavior is covered by tests.

### Story E5-S2 — Audit retention and access controls
**As a** compliance stakeholder, **I want** durable audit logs and role-based access, **so that** actions are traceable.

**Acceptance Criteria**
- Audit logs exist for create/update/publish/deprecate/archive/evaluate actions.
- Retention duration is configurable and enforced.
- Role checks for reader/editor/admin are implemented on protected endpoints.
- Unauthorized access attempts are logged.

---

## Epic E6 — Reliability and Performance SLOs (P0)

### Story E6-S1 — Evaluation latency SLO instrumentation
**As a** product owner, **I want** latency SLO tracking, **so that** user experience remains acceptable.

**Acceptance Criteria**
- P50/P95/P99 latency metrics captured for evaluation endpoints.
- SLO thresholds are defined and dashboarded.
- Breach alerts are configured.
- SLO reports are accessible to product and engineering.

### Story E6-S2 — Request tracing and error observability
**As a** developer, **I want** traceable request flows, **so that** incidents are diagnosable.

**Acceptance Criteria**
- Request IDs are generated/passed through all API responses and logs.
- Structured error codes are consistent with API error contract.
- Top error classes and rates are visible in dashboard views.
- Logs correlate resolver outcomes with evaluation request IDs.

---

## Epic E7 — Cost Guardrails (P1)

### Story E7-S1 — Per-run and monthly budget enforcement
**As an** admin, **I want** spend constraints, **so that** evaluations do not exceed budget.

**Acceptance Criteria**
- Per-run budget cap blocks or truncates evaluation based on policy.
- Monthly soft cap emits alerts and policy-based enforcement.
- Usage ledger supports reporting by day/week/month.
- Error messaging clearly communicates budget-related failures.

### Story E7-S2 — Model-tier allowlist and override workflow
**As an** owner, **I want** model governance with exceptions, **so that** cost and quality tradeoffs are controlled.

**Acceptance Criteria**
- Allowlist blocks disallowed model tiers.
- Authorized override path exists and is audited.
- Override events include reason, actor, timestamp.
- Dashboard surfaces override frequency and impact.

---

## Epic E8 — Initial Integrations (Ticketing + Docs) (P1)

### Story E8-S1 — Ticketing integration events
**As a** QA lead, **I want** evaluation/lifecycle events in ticketing, **so that** governance work is trackable.

**Acceptance Criteria**
- `POST /v1/integrations/tickets/events` publishes normalized event payloads.
- Events include action type, target ID, actor, timestamp, and status.
- Delivery failures are retried with dead-letter logging.
- Integration credentials are stored securely.

### Story E8-S2 — Documentation publishing integration
**As a** product stakeholder, **I want** persona and evaluation summaries in docs/wiki, **so that** teams can review outcomes asynchronously.

**Acceptance Criteria**
- `POST /v1/integrations/docs/publish` supports publish of persona snapshots and evaluation summaries.
- Output format is consistent and templated.
- Publish history is auditable.
- Failed publishes are visible and retryable.

---

## Cross-Cutting Definition of Done
- API contract documented and example payloads updated.
- Unit tests + integration tests pass for new behavior.
- Resolver and lifecycle paths have explicit negative tests.
- Audit and observability hooks included for each new endpoint.
- Security review completed for data handling changes.

## Recommended Delivery Sequence
1. E1 + E2 (core registry + governance correctness)
2. E3 + E4 (rosters and evaluation outcomes)
3. E5 + E6 (security baseline + reliability)
4. E7 + E8 (cost controls + external integrations)

## Candidate V1.1 Deferrals (if needed)
- Advanced taxonomy tooling for roster metadata.
- More complex rubric calibration and weighting workflows.
- Multi-tenant architecture uplift.
- Expanded integration catalog (CI, Copilot tooling, analytics-first).
