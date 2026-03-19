# Persona Registry API — Design Decision Template

Use this template to answer discovery questions in a decision-ready format.

## How to use
- Keep each decision short and explicit.
- Capture owner and date so accountability is clear.
- Include tradeoffs so future revisions are easier.
- Link affected spec sections for quick updates.

---

## Decision Record

### D-001 — Primary V1 Outcome = Better Response Quality
- **Question Ref:** Q1 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Prioritize improved response quality as the primary v1 business outcome.
- **Why this decision:** Higher-quality outputs create immediate trust and increase adoption of persona-driven workflows.
- **Alternatives considered:**
  - Option A: Prioritize faster persona testing.
  - Option B: Prioritize lower business risk.
- **Tradeoffs / Risks:** Improvements may take longer to measure than operational metrics (speed/cost).
- **Mitigations:** Define clear quality rubrics and baseline comparisons in evaluation runs.
- **Impact on scope (v1 / v1.1 / later):** v1 emphasizes evaluation quality signals and reusable persona consistency.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define quality rubric fields for evaluation results.
  - [ ] Add baseline-vs-persona comparison guidance.

### D-002 — First User Roles = Prompt Engineer, Developer, QA Lead
- **Question Ref:** Q2 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Target first-month adoption for prompt engineers, developers, and QA leads.
- **Why this decision:** These roles can operationalize persona authoring, integration, and quality validation quickly.
- **Alternatives considered:**
  - Option A: Product-manager-first rollout.
  - Option B: Broad all-role rollout at launch.
- **Tradeoffs / Risks:** Non-technical stakeholders may be underrepresented in early feedback.
- **Mitigations:** Include stakeholder-facing summary outputs from evaluation reports.
- **Impact on scope (v1 / v1.1 / later):** v1 API and docs prioritize technical users and test workflows.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define role-specific example workflows.
  - [ ] Add onboarding examples for each role.

### D-003 — Must-Have Workflow = Import Persona -> Roster Test -> Compare Results
- **Question Ref:** Q3 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Prioritize end-to-end support for importing personas, running roster tests, and comparing results.
- **Why this decision:** This directly validates business value by turning persona assets into measurable testing outcomes.
- **Alternatives considered:**
  - Option A: Create/publish/evaluate single persona only.
  - Option B: Governance-first rollout without comparison tooling.
- **Tradeoffs / Risks:** Comparison capability can add complexity to result models and UX.
- **Mitigations:** Start with simple side-by-side metrics and transcript links.
- **Impact on scope (v1 / v1.1 / later):** v1 must include roster-aware evaluation and comparison-ready result schema.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Add import contract to API surface.
  - [ ] Define minimal comparison response payload.

### D-004 — Success Metrics = Stakeholder Adoption + Reusable Persona Count
- **Question Ref:** Q4 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Track success primarily with stakeholder trust/adoption and number of reusable personas.
- **Why this decision:** Adoption proves usability while reusable assets demonstrate compounding value.
- **Alternatives considered:**
  - Option A: Time-to-test reduction as primary metric.
  - Option B: Evaluation pass-rate as primary metric.
- **Tradeoffs / Risks:** Adoption metrics can be noisy without clear usage definitions.
- **Mitigations:** Define active usage thresholds and persona reuse criteria.
- **Impact on scope (v1 / v1.1 / later):** v1 must capture usage analytics and persona reuse metadata.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define “active stakeholder usage” metric.
  - [ ] Add reusable persona tracking fields/events.

### D-005 — Scope-Cut Keepers = Versioning/Latest, Lifecycle, Evaluation Runs
- **Question Ref:** Q5 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** If scope is reduced, preserve (A) persona versioning + latest resolution, (B) publish/deprecate lifecycle, and (D) evaluation runs.
- **Why this decision:** These capabilities preserve core product value: trustworthy persona retrieval and measurable testing.
- **Alternatives considered:**
  - Option A: Keep rosters over lifecycle controls.
  - Option B: Keep audit-only controls over evaluations.
- **Tradeoffs / Risks:** Deferring roster enhancements may limit advanced batch testing early.
- **Mitigations:** Support single-target evaluations first and reintroduce richer roster capabilities in v1.1.
- **Impact on scope (v1 / v1.1 / later):** v1 remains lean and outcome-focused; non-core features can be deferred.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Mark non-core features as v1.1 in roadmap.
  - [ ] Add cutline note to milestone planning.

### D-006 — Published Persona Mutability (Pending)
- **Question Ref:** Q6 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Proposed
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Proposed default is strict immutability after publish; any changes require a new version.
- **Why this decision:** Immutability improves reproducibility, auditability, and trust in evaluation results over time.
- **Alternatives considered:**
  - Option A: Immutable except emergency metadata hotfix.
  - Option B: Editable with full audit trail.
- **Tradeoffs / Risks:** Operational friction for small typo or metadata fixes.
- **Mitigations:** Add lightweight clone-and-bump workflow and optional redirect note in changelog.
- **Impact on scope (v1 / v1.1 / later):** v1 stays stable and testable; limited hotfix policy can be introduced later if needed.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Confirm final mutability policy (A/B/C).
  - [ ] Update validation and publish workflow accordingly.

### D-007 — Publish Approval Model = Single Owner
- **Question Ref:** Q7 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Use single-owner approval for publishing persona versions in v1.
- **Why this decision:** Fastest path to delivery and lower process overhead during early product iteration.
- **Alternatives considered:**
  - Option A: Dual approval (author + reviewer).
  - Option B: Role-based policy by persona type.
- **Tradeoffs / Risks:** Increased risk of inconsistent quality or governance drift.
- **Mitigations:** Require changelog + publish checklist and maintain full audit logging.
- **Impact on scope (v1 / v1.1 / later):** v1 prioritizes speed; stronger approval controls can be added in v1.1.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define owner role permissions clearly.
  - [ ] Add publish checklist to docs.

### D-008 — Deprecation Policy = Manual Archive (No Auto-Archive)
- **Question Ref:** Q8 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Deprecated persona versions remain callable until explicitly archived by an authorized owner.
- **Why this decision:** Provides flexibility while product usage patterns and migration behavior are still being learned.
- **Alternatives considered:**
  - Option A: Auto-archive after fixed window (30/60/90 days).
  - Option B: Hard retirement schedule by policy.
- **Tradeoffs / Risks:** Deprecated versions may remain in use longer than ideal.
- **Mitigations:** Add dashboard warning and “deprecated in use” reporting for follow-up.
- **Impact on scope (v1 / v1.1 / later):** v1 favors operational flexibility; lifecycle automation can be layered later.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Add deprecated-usage analytics requirement.
  - [ ] Define archive authorization rule.

### D-009 — Roster Organization = Hybrid (Function + Task Tags)
- **Question Ref:** Q9 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Organize rosters using a hybrid model that supports both business function and task-type classification.
- **Why this decision:** Hybrid tagging improves discoverability and reusability across teams and use cases.
- **Alternatives considered:**
  - Option A: Function-only roster organization.
  - Option B: Task-only roster organization.
- **Tradeoffs / Risks:** Potential taxonomy sprawl and inconsistent tagging.
- **Mitigations:** Establish a controlled tag glossary and linting/validation for roster metadata.
- **Impact on scope (v1 / v1.1 / later):** v1 includes minimal hybrid metadata fields; advanced taxonomy tooling can follow later.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define required roster metadata fields.
  - [ ] Publish initial controlled vocabulary.

### D-010 — Evaluation Judging = Hybrid Weighted Scoring
- **Question Ref:** Q10 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Use hybrid evaluation: automated scoring plus human rubric with configurable weights.
- **Why this decision:** Combines scale and consistency from automation with nuanced judgment from human review.
- **Alternatives considered:**
  - Option A: Human-only rubric scoring.
  - Option B: Automated-only scoring.
- **Tradeoffs / Risks:** Increased implementation complexity and weighting disputes.
- **Mitigations:** Start with a simple default weighting profile and versioned rubric definitions.
- **Impact on scope (v1 / v1.1 / later):** v1 includes basic weighted score aggregation; advanced calibration can be deferred.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define default weight profile.
  - [ ] Add rubric version field to evaluation model.

### D-011 — Unacceptable Failures = Wrong Resolution + High Latency
- **Question Ref:** Q11 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Treat wrong persona/version resolution and high evaluation latency as critical failures.
- **Why this decision:** Correct persona targeting preserves trust and validity; latency directly affects adoption and workflow fit.
- **Alternatives considered:**
  - Option A: Missing audit trail as highest-priority failure.
  - Option B: Silent deprecated version usage as highest-priority failure.
- **Tradeoffs / Risks:** Strong SLO commitments may increase infra and operational cost.
- **Mitigations:** Add strict resolver checks, caching strategy, and measurable latency SLOs.
- **Impact on scope (v1 / v1.1 / later):** v1 must include resolver correctness tests and performance telemetry.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define resolver correctness contract tests.
  - [ ] Define latency SLO targets by endpoint.

### D-012 — Security/Compliance Priorities = PII, Audit Retention, Access Control
- **Question Ref:** Q12 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Top-3 priorities for v1 are (A) PII controls, (B) audit retention, and (C) team/tenant access control.
- **Why this decision:** This set creates a practical baseline for trust, traceability, and safe operational access.
- **Alternatives considered:**
  - Option A: Include data residency in top-3 from day one.
  - Option B: Prioritize audit/data residency over access controls.
- **Tradeoffs / Risks:** If data residency is required early, deferring it could block enterprise rollout.
- **Mitigations:** Confirm customer/region requirements before implementation freeze.
- **Impact on scope (v1 / v1.1 / later):** v1 includes baseline controls; advanced compliance overlays can follow.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [x] Confirm final Q12 top-3 choices.
  - [ ] Add explicit data-handling policy section.

### D-013 — Tenant Model = Single-Tenant V1
- **Question Ref:** Q13 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Use pure single-tenant architecture for v1 delivery.
- **Why this decision:** Prioritizes speed and simplicity for initial launch and reduces implementation risk.
- **Alternatives considered:**
  - Option A: Single-tenant v1 only.
  - Option B: Full multi-tenant v1.
- **Tradeoffs / Risks:** Future multi-tenant support may require deeper refactoring.
- **Mitigations:** Keep interfaces clean and avoid leaking tenant assumptions into API contracts.
- **Impact on scope (v1 / v1.1 / later):** v1 is optimized for rapid delivery; multi-tenant becomes an explicit v1.1+ project.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [x] Confirm Q13 choice (A/B/C).
  - [ ] Add single-tenant assumptions to storage/auth sections.

### D-014 — First Integrations = Ticketing + Docs
- **Question Ref:** Q14 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Prioritize initial integrations with ticketing systems and documentation/wiki platforms.
- **Why this decision:** These channels improve governance visibility and adoption in existing team workflows.
- **Alternatives considered:**
  - Option A: Copilot tooling + CI as first integrations.
  - Option B: Analytics-first integration strategy.
- **Tradeoffs / Risks:** Delaying Copilot/CI integration may slow engineering automation.
- **Mitigations:** Define integration contracts so Copilot/CI can be added in v1.1 with minimal rework.
- **Impact on scope (v1 / v1.1 / later):** v1 favors process adoption and documentation traceability.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define webhook/event payloads for ticket updates.
  - [ ] Define docs publishing/export format.

### D-015 — Cost Guardrails = Per-Run + Monthly Cap + Model Allowlist
- **Question Ref:** Q15 from [design-discovery-questions.md](design-discovery-questions.md)
- **Status:** Approved
- **Decision Owner:** Product/Engineering Lead (TBD)
- **Date:** 2026-03-18
- **Decision:** Apply policy A + C: per-run budget cap, monthly soft cap, and model-tier allowlist.
- **Why this decision:** Combines tactical spend control with strategic model governance.
- **Alternatives considered:**
  - Option A: Monthly cap only.
  - Option B: Allowlist only.
- **Tradeoffs / Risks:** May block some high-value evaluations if caps are set too low.
- **Mitigations:** Add override workflow for authorized users with audit logging.
- **Impact on scope (v1 / v1.1 / later):** v1 includes guardrails without requiring complex cost forecasting.
- **Affected spec sections:**
  - [persona-registry-design-spec.md](persona-registry-design-spec.md)
- **Follow-up actions:**
  - [ ] Define default budget thresholds.
  - [ ] Define override permissions and audit events.

---

## Quick Capture Sheet (One-line per question)

| Q# | Decision summary | Owner | Target date | Spec section to update |
|---|---|---|---|---|
| Q1 | Primary outcome is better response quality | Product/Engineering Lead (TBD) | 2026-03-18 | Goals, Evaluations, Observability |
| Q2 | First users: prompt engineer, developer, QA lead | Product/Engineering Lead (TBD) | 2026-03-18 | Goals, API Surface, Docs |
| Q3 | Must-have flow: import persona -> roster test -> compare results | Product/Engineering Lead (TBD) | 2026-03-18 | API Surface, Evaluations, Rosters |
| Q4 | Success metrics: stakeholder adoption + reusable persona count | Product/Engineering Lead (TBD) | 2026-03-18 | Goals, Observability |
| Q5 | Scope-cut keepers: versioning/latest, lifecycle, evaluation runs | Product/Engineering Lead (TBD) | 2026-03-18 | Versioning, Lifecycle, Milestones |
| Q6 | Proposed: strict immutable after publish (pending final decision) | Product/Engineering Lead (TBD) | 2026-03-18 | Versioning, Validation Rules |
| Q7 | Publish approval uses single owner in v1 | Product/Engineering Lead (TBD) | 2026-03-18 | Auth/Access, Lifecycle |
| Q8 | Deprecated versions are manually archived only | Product/Engineering Lead (TBD) | 2026-03-18 | Lifecycle, Operations |
| Q9 | Roster model is hybrid: function + task classification | Product/Engineering Lead (TBD) | 2026-03-18 | Rosters, Search/Filtering |
| Q10 | Evaluation uses hybrid weighted scoring | Product/Engineering Lead (TBD) | 2026-03-18 | Evaluations, Results Schema |
| Q11 | Critical failures: wrong resolution and high latency | Product/Engineering Lead (TBD) | 2026-03-18 | Resolver Logic, SLOs, Observability |
| Q12 | Top priorities: PII controls, audit retention, access control | Product/Engineering Lead (TBD) | 2026-03-18 | Security, Compliance, Audit |
| Q13 | Tenant model: single-tenant v1 | Product/Engineering Lead (TBD) | 2026-03-18 | Storage, Auth/Access |
| Q14 | First integrations: ticketing + docs/wiki | Product/Engineering Lead (TBD) | 2026-03-18 | Integrations, Operations |
| Q15 | Cost guardrails: per-run cap + monthly soft cap + model allowlist | Product/Engineering Lead (TBD) | 2026-03-18 | Evaluations, Policy Controls |

---

## Prioritization Rubric (Optional)

Score each major decision from 1 (low) to 5 (high):
- **Business impact:**
- **Delivery effort:**
- **Risk reduction:**
- **Time sensitivity:**

Use score notes to justify sequencing in roadmap updates.
