# AURS ∞ — Human × AI Command Front · Operating Contract v1

Date: 2026-11-23 | Branch-only prototype | Public-safe documentation

## Mission
Serve customers worldwide through original design, ethical manufacturing, trustworthy business operations, and clear human accountability. AURS coordinates, SANTRAM INDUSTRIES manufactures, STYNSPARK presents premium consumer-facing creation. Human purpose and judgment guide AI-assisted research and drafts; no person, market, data, or external system is controlled without permission.

## One-tap protocol
INPUT: user click, contextual voice/text directive, or NEXT.
CONTEXT: explicitly selected brand, workflow, stage, approved references, locally available notes.
PROCESS: retrieve only accessible authorized context; distinguish verified facts from drafts; propose the most valuable feasible next action; compute cost/benefit/risk; prepare tangible output.
OUTPUT: one concise deliverable plus one clearly actionable next choice.
PROHIBITED CLAIMS: no mind reading; no unlimited access to historic chats; no autonomous 24/7 operation absent a verified scheduler, backend and permissions.

## Six workflows
1. Creation: brief -> original directions -> feasibility -> costing/QC -> approval -> production release.
2. Quotation: specs -> bill of materials -> validation -> pricing choices -> approval -> send.
3. Sales: ICP -> offer -> verified leads -> outreach draft -> approval -> authorized contact.
4. Production: order -> materials -> schedule -> QC -> release -> dispatch approval.
5. Marketing: positioning -> UX -> assets -> test plan -> content approval -> authorized publish.
6. Global trade: market -> legal checks -> capacity -> deal terms -> approval -> authorized transaction.

## Action security matrix
- GREEN / local drafts: design brief, costing, original concept, checklists, planning, prompt compilation.
- AMBER / human review: public claim, price quote, customer content, supplier/lead verification, external data transfer.
- RED / explicit per-action permission and verified connected system: payment, ad spend, public publication, email/WhatsApp send, contracts, access to sensitive sources, production, shipping, deletion, and non-reversible actions.
Local approval records are not proof that an external action occurred.

## Code and data boundaries
- Prototype: aurs-command-front.html is a static mobile-first, localStorage-based deterministic workflow router. It does not call ChatGPT or any AI model by API, send customer data or perform background tasks. It produces context-rich commands to submit in an active ChatGPT chat.
- Browser-local notes and JSON backups can contain sensitive data: treat as confidential; do not commit these to any public repository.
- Existing apoxy-stynspark/main and existing deployed services are untouched. This isolated feature branch has not been publicly deployed or merged.
- No paid resources or recurring subscriptions were activated in this change.

## Deployment path (not yet completed)
A. Review the front in an isolated environment with real mobile/keyboard tests.
B. Add private authentication, access control, encrypted data at rest where applicable, tenant isolation, audit logs and secure backups.
C. Connect authorized data sources with per-connector scopes and consent; show sources and freshness.
D. Implement protected server-side action orchestration and per-action approval ledger, idempotency and rollback strategy.
E. Verify costs, rates, compliance, privacy policy, India/global tax/export/consumer requirements, and publishing permissions.
F. Only after explicit user approval: deploy private staging, run production tests, then release chosen public modules.
