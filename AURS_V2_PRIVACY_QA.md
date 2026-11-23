# AURS ∞ Business Command Engine — NEXT 02

Date: 2026-11-23 | Branch: feature/aurs-human-ai-command-front-20261123

## What changed
New stand-alone \`aurs-command-front-v2.html\` (v1 left intact). The file is designed for a private, local browser evaluation, not production or public deployment.

* Brand filters: AURS / SANTRAM INDUSTRIES / STYNSPARK.
* Local project/order records, owner role, due date, workflow stage, quantity, category, internal notes, manually entered customer approval/dispatch status.
* Per-project file-presence checklist (ticks only, no files uploaded).
* Offline pricing estimator: unit cost = material × (1 + wastage/100) + labour + other. Unit selling price ex tax = unit cost / (1 - gross margin/100). Manual GST is applied separately. No rates are represented as verified.
* NEXT produces a stage- and approval-aware command ready to copy into ChatGPT. The UI itself is deterministic, not an AI backend.
* Overdue, approval-blocked or rework projects are prioritized in the local project listing.
* JSON backup and import, no remote network requests, no tracking libraries, no public external action.
* User-entered strings are displayed with textContent rather than inserted as HTML.

## Trust boundaries
1. This GitHub repository is **PUBLIC**; the prototype source is visible. Do not commit customer data, JSON backups, API keys or secrets.
2. Browser localStorage is unencrypted and device/browser-bound. A shared mobile device is not suitable for customer-identifying data. Use aliases only.
3. UI states "approved", "sent", file ticks and costing entries are **self-reported**; they are not verified proof. Never infer an order is safe to manufacture or ship from one local flag.
4. This implementation has no account authentication, private database, access control, tenant isolation, secure backend, server-side enforcement, connection to ChatGPT API, payments, CRM sync, autonomous mining or 24×7 job runner.
5. No branch was merged, no paid service or production publishing activated.

## QA checklist before any private deployment
- [ ] Open HTML locally on Android Chrome and desktop browser; test brand switching, inputs, mobile keyboard, button focus.
- [ ] Add 2 fictitious aliases across brands; refresh and confirm local persistence.
- [ ] Edit fields; check per-piece and total estimates, margin math, zero-cost case, invalid quantities.
- [ ] Check unapproved production NEXT always blocks external release.
- [ ] Test NEXT, copied prompt, JSON export/import (with *only fictitious data*), empty data, deletion confirmation.
- [ ] Confirm no outgoing network requests in devtools.
- [ ] Add automated regression tests and a real private staging boundary before any real customer-data use.

## Next engineering milestone (NOT YET DONE)
Secure private staging with login, private database, encrypted backups, audit trail, server-side per-action approval and role-based authorization. First verify user-owned hosting/account, budget and compliance. Do not deploy publicly, buy services or change \`main\` without separate explicit authorization.
