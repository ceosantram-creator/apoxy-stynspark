# SANTRAM INDUSTRIES — AI Operating System INFINITY
Version: 2.0 checkpoint
Date: 2026-11-02
Repository: ceosantram-creator/apoxy-stynspark
Implementation branch: android-clean-rebuild-v2
Protected branch: main (do not modify)

## Product goal
One silent-by-default, local-first Android command center for personal workflows and SANTRAM INDUSTRIES operations. The product must distinguish implemented capabilities from planned integrations and never claim access or automation that is not active.

## Operating rules
- Silent output by default; no unsolicited text-to-speech.
- Microphone capture, if added, must be user-initiated, visibly active and permissioned. No covert or ambient always-on recording.
- No reading private notifications, contacts, files, messages or location without a clear feature purpose and explicit Android permission.
- Consequential actions (sending messages, payments, deletion, account changes, invoice issue) require user confirmation.
- Financial records are local-first and backed up only to user-selected destinations.
- Never invent customer details, GSTIN, invoice numbers, payment records or signatures.
- Never modify GitHub main; work only on android-clean-rebuild-v2 until review.

## Current implemented Android checkpoint
- Jetpack Compose Android 15 application shell.
- Silent Mode preference stored locally.
- Central dashboard counters for tasks, customers and invoice drafts.
- Personal task inbox with local persistence and completion toggles.
- Business customer register with name, phone and optional GSTIN.
- Internal invoice draft register with customer, description and amount.
- User-triggered JSON backup export and restore using Android document picker.
- No microphone, notification-listener, accessibility or location permissions requested.

## Explicitly not implemented yet
- Room database, encrypted database/key management and robust migrations.
- AI provider, LLM reasoning, automatic intent/date parsing or agent execution.
- Voice capture and speech-to-text.
- Scheduled reminders, alarms or background monitoring.
- GST calculation, compliant invoice sequence, immutable issued invoices, PDF generation, e-invoice/e-way bill or payment reconciliation.
- Cloud backend, authentication, multi-device sync, Google Drive connector or WhatsApp/Gmail integrations.
- Notification summaries or accessibility automation.

## Target architecture
### Android client
- Kotlin + Jetpack Compose.
- MVVM/repository architecture.
- Room for structured offline-first data; DataStore for preferences.
- WorkManager for deferrable sync and backup jobs.
- User-initiated speech recognition with visible lifecycle and Android permission.
- Android Sharesheet and Storage Access Framework for file import/export.
- Narrow opt-in notification/accessibility integrations only after privacy review.

### Business core
- Customer master and validated address/GST profile.
- Product/service catalogue and HSN/SAC.
- GST calculator with CGST/SGST/IGST, place-of-supply validation and rounding tests.
- Separate estimate/proforma and tax-invoice counters with collision prevention.
- Payment ledger and outstanding balance reconciliation.
- Fixed PDF template with embedded fonts, wrapping/overflow checks and visual regression tests.
- Immutable issued-document snapshot and audit log.

### Cloud and dashboard
- Optional authenticated API and PostgreSQL with tenant/row-level access controls.
- Encrypted transport, explicit account connection and conflict resolution.
- User-authorized Google Drive backup; no OAuth secrets in source control.
- Human approval for consequential actions.

## Delivery phases
1. Foundation: local tasks, customer master, invoice drafts, silent preference, JSON backup/restore. (Implemented checkpoint; CI verification required.)
2. Data hardening: Room migration, encrypted storage, validation, automated backup/restore tests.
3. Personal automation: explicit voice capture, date/time parsing, reminders and notification controls.
4. Business operations: catalogue, tax engine, invoice PDF, payments and audit trail.
5. AI core: server-side provider adapter, prompt/intent router, tool permissions, cost controls and approval gates.
6. Integrations: optional Google Drive, Gmail, WhatsApp and mobile bridge via official user-authorized paths.
7. Release: signing, device compatibility, security/privacy review, offline and restore tests.

## Android 15 constraints
- Microphone access requires RECORD_AUDIO and is subject to while-in-use restrictions.
- Start any microphone foreground service while app is visible and user initiates capture.
- Do not start microphone foreground services from BOOT_COMPLETED.
- Foreground services require a user-visible notification.
- WorkManager is for deferrable work, not continuous microphone capture.

## Release quality gates
- Unit tests for data validation, GST arithmetic, rounding, numbering and balance calculations.
- UI tests for task persistence, backup/restore and voice lifecycle.
- PDF regression tests for clipping, font embedding, page count and content accuracy.
- Offline, migration, restore and failure-recovery tests.
- CI build pass, downloadable artifact, and real-device install/smoke test before calling a build release-ready.
