# AURS ∞ / NEXT 03 — Mobile Functional QA + Private Staging Feasibility
Date: 23 November 2026
Repository: ceosantram-creator/apoxy-stynspark (PUBLIC)
Isolated branch: feature/aurs-next03-qa-secure-staging-20261123
Decision: **NO-GO for real customer data, production deployment, payment or public launch. GO for a local-only demonstration with fictitious internal project aliases.**

## 1. Evidence of implementation and QA

Files inspected and updated on the isolated branch:
- \`aurs-command-front-v2.html\`: local-only HTML/JS command front.
- \`tests/aurs-next03-functional.test.cjs\`: dependency-free simulated DOM regression test. Run \`node --test tests/aurs-next03-functional.test.cjs\` after cloning the branch.
- \`db/next03_private_schema_blueprint.sql\`: **not deployed**, read-only-by-default Postgres/RLS scaffold and append-only event controls for expert review.

Actual execution this turn: the previously observed 15 in-memory functional assertions passed before the regression file was committed. The saved regression harness was also executed against the updated HTML using a JavaScript DOM simulator: **9/9 scenarios passed**, zero failures. JavaScript syntax parsed successfully. No secrets, customer PII or private backup files were written to GitHub. All tests used fictitious data.

Scenarios passing:
1. HTML/JS syntax, explicit \`connect-src 'none'\` policy, no app network request API in local script, mobile breakpoint + 44px chip target.
2. Empty dashboard renders and handles no active project.
3. Project creation persists locally.
4. Formula: material ₹10, wastage 10%, labour ₹5, other ₹2 = cost ₹18; gross margin 25% -> sale before GST ₹24; manual GST 18% -> ₹28.32 each; qty 100 -> ₹2,832.
5. Bad calendar dates (e.g. 2026-02-30) rejected; text-like HTML inserted via \`textContent\`.
6. Production stage + pending approval produces STOP/verify outcome.
7. Browser-local records log stage and approval state edits.
8. File checklist edits create local history.
9. Changing brand clears the previous NEXT prompt/selection.
10. Imported duplicate project IDs are rejected.

Fixes committed:
- Hardened prototype CSP to block network \`connect\` and external resources, without breaking the inline local script.
- Added explicit local-only change log (not a tamper-proof ledger).
- Added strict calendar date check and deduplication of imported IDs.
- Prevented cross-brand active project selection and stale NEXT prompt when switching.
- Treats imported project names and notes as untrusted data in generated AI commands.
- Narrow-screen checklist becomes a single column, cost output wraps and tap-target size improved.
- Logged checklist status edits; retained confirmation for deletions/record replacements.

**NOT tested:** Real Android Chrome UI, font rendering and 360/390 px screenshots, keyboard overlap, TalkBack gestures, Android download/import permissions, touch latency, offline refresh with browser storage restrictions, multi-device sync, external pen-testing, rate limiting, authenticated database RLS, production performance. The DOM simulator cannot establish these results.

## 2. Critical security and privacy findings

| Area | Current implementation | Risk / required gate |
| --- | --- | --- |
| Login | None. Browser localStorage | Critical for shared/real client use; invite-only auth, MFA where supported and short sessions |
| Database | None. Browser-local JSON | Critical; isolated Postgres with org_id enforcement and RLS |
| Approval ledger | Local event change list; editable and importable | Critical; append-only server transaction, actor/time/evidence and policy-enforced decisions |
| Backup | Plain JSON export/import | Critical; encrypted scheduled off-site backups + restoration test. Never put export in public repo |
| Tenant isolation | Only brand filters in UI | Critical; filters are not authorization. Enforce membership/role on every server query |
| Secrets | No API keys embedded in the front | Maintain all server credentials in provider secret manager, least privilege, rotation |
| Logging | Browser local, easy to change | Real signed/audited server events, limited retention and no PII in free-text logs |
| Public source repository | Code is public | Never store passwords, customer records, backup JSON, tokens or pricing trade secrets on this branch |
| Network | CSP \`connect-src 'none'\`; no app network API | Local-only demo; security of hosted version requires response headers and review of all assets |
| Operational actions | Text-only NEXT prompt, no external execution | Require explicit human authorization, server policy, idempotency keys, verification and records |

Approval status in the UI is **self-reported** and does not constitute customer consent, a contract, production clearance or dispatch authority.

## 3. Staging architecture (feasible, NOT implemented)

1. **Private code source:** A separate *private* repository / secure staging pipeline (not this currently public repo) with protected default branch, security scanning, review controls, no customer data committed. Do not rewrite or merge existing \`main\`.
2. **Private site gate:** Cloudflare Pages only after protecting **every** staging and preview hostname with Cloudflare Access or an equivalent private gateway. A default \`pages.dev\` URL is **not automatically private**. Default deny; explicitly allow identified testers.
3. **Identity:** Invitation-only Supabase Auth or equivalent, MFA as applicable; no anonymous users for business data, session expiry/revocation, brute-force and password recovery tests.
4. **Database:** Postgres with \`org_id\` foreign keys, member roles, RLS on every data table and storage bucket. RLS policies must be tested against cross-company access attempts.
5. **Approval service:** Server-side only action request -> verified evidence -> separate decision by authorized person -> immutable event -> idempotent execution. High-impact actions must reject self-approval if policy calls for two-person control. Client UI may request an action but cannot finalize one.
6. **Backup:** Encrypted off-site backup with retention, restore drills and audit. On Supabase Free, automatic database backups are not included; manual exports are not production-ready.
7. **Monitoring and privacy:** Security logs, alerts, breach response, retention/deletion policy, provider agreements, appropriate India / foreign transfer legal review before customer PII, and scoped access to connectors.

### Minimal model (proposed)
\`users\` (identity provider) -> \`memberships(user_id, org_id, role)\` -> \`organizations\` -> \`projects\` -> \`approval_requests\` -> \`approval_events\` -> \`audit_events\`.
All sensitive writes happen through authenticated authorization logic, not direct browser updates to approval or audit tables.

## 4. Costs as checked on 23 November 2026

| Approach | New base platform subscription | What it really includes | Missing / variable costs |
| --- | --- | --- | --- |
| Current local prototype | **₹0/day, ₹0/month incremental** | Offline HTML and local JSON, no hosted auth or sync | Time and testing, local data-loss risk |
| Experimental private staging on free tiers | **$0/month platform baseline IF within free quotas** | GitHub Free private repo; Cloudflare Pages Free + free Access for eligible small team; Supabase Free (500 MB database, Auth) | **No Supabase automatic backups**, inactivity pausing, setup, domain, email/SMS, compliance, API, potential overages |
| Paid managed DB baseline | **Supabase Pro from $25/month** before taxes and extras | Managed DB/Auth + automatic backup retention listed as 7 days | Cloudflare extra usage, email/SMS, domain, model API, egress, tax/FX and any larger backup/PITR |

No subscription or paid resource was created. No currency conversion has been assumed. Existing ChatGPT Plus does **not** pay for hosted API usage. Do not purchase an upgrade solely to escape chat usage limits.

Verified official source documents (pricing/features change; recheck before subscribing):
- https://supabase.com/pricing
- https://supabase.com/docs/guides/platform/billing-on-supabase
- https://developers.cloudflare.com/pages/platform/limits/
- https://www.cloudflare.com/sase/products/access/
- https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

## 5. Release blockers and go/no-go

**P0 before handling real customer data**
- [ ] Owner-approved private infrastructure/accounts and exact budget, providers and data residency.
- [ ] Verify staging and every preview hostname is authenticated and cannot bypass Access.
- [ ] Backend login / MFA / session lifecycle + unit/integration tests.
- [ ] Server-side RLS and hostile cross-tenant tests.
- [ ] Immutable, actor-attributed approval event trail and external approval evidence.
- [ ] Encrypted backup and successfully restored sample database.
- [ ] Legal privacy review: Indian DPDP applicability, retention, breach process, overseas processors, GST/export laws where relevant.
- [ ] Rate limits, error handling, no secrets in client, dependency/CI scan.

**P1 mobile testing**
- [ ] Real Android Chrome at 360px and 390px viewport: no horizontal overflow, forms and long rupee figures remain legible.
- [ ] 200% text zoom, landscape orientation, TalkBack labels and focus order.
- [ ] Keyboard-open entry for order fields, touch target and form save.
- [ ] Offline refresh and JSON import/export on Android with fictitious data.

**Current decision: Local-only prototype can be demonstrated with dummy data. Secure private staging NOT deployed; production and public launch explicitly NOT authorized.**

Suggested next human gate: authorize creating a *separate empty private staging repository/environment* without adding customer data, and only after reviewing ownership/costs. That is a future step, not undertaken here.
