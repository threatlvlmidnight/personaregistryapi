# Persona Registry API — Design Discovery Questions

Use these questions to flesh out the product and delivery design before implementation.

## Business Outcomes & Scope
1. What is the primary business outcome for v1: faster persona testing, better response quality, lower risk, or all three (rank in order)?
2. Who are the first 2–3 user roles (e.g., prompt engineer, product manager, QA lead), and what must each role do in the first month?
3. What is the “must-have” workflow you want working end-to-end first: create persona -> publish version -> run evaluation -> compare results?
4. How will we define success at 30/60/90 days (specific metrics like time-to-test, number of reusable personas, evaluation pass rate)?
5. If we had to cut scope by 40% for speed, which capabilities stay no matter what?

## Governance & Lifecycle
6. Should persona versions be immutable after publish with strict governance, or do you want emergency edits for critical fixes?
7. What approval model do you want for publishing personas: single owner, dual approval, or role-based policy?
8. What is your deprecation policy: how long should deprecated persona versions remain callable before archive?

## Roster & Evaluation Design
9. For rosters, do you want them tied to business functions (sales, compliance, support) or to task types (risk review, vendor eval, executive brief)?
10. How should evaluations be judged: human rubric only, automated scoring only, or hybrid with weighted criteria?
11. What failure is unacceptable in production (wrong persona resolution, stale version usage, missing audit trail, evaluation latency)?

## Security, Compliance & Platform
12. What are your top compliance/security constraints (PII handling, audit retention window, access by team/tenant, data residency)?
13. Do you need tenant isolation from day one (multiple clients/business units), or can v1 be single-tenant?
14. What systems must this integrate with first (Copilot session tooling, CI pipelines, ticketing, docs, analytics)?
15. What pricing/cost guardrails matter for evaluations (per-run budget, monthly cap, model tier restrictions)?
