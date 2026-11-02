# SANTRAM PERSONAL AI INFINITY — Android 15 Architecture
Version: 1.0
Date: 2026-11-02
Repository: ceosantram-creator/apoxy-stynspark
Implementation branch: android-clean-rebuild-v2
Protected branch: main (do not modify)

## Product goal
Build one silent, text-first Android assistant and central dashboard combining:
1. Personal/mobile workflow management.
2. SANTRAM INDUSTRIES business operations.
3. User-approved memory, file organization, and backup.
4. Reliable document generation and verification.

## Non-negotiable operating rules
- Silent output by default: no text-to-speech or unsolicited spoken replies.
- Voice capture is user-initiated and visibly active; no covert or ambient always-on recording.
- Show a persistent foreground notification while an approved microphone capture session is active.
- Never claim continuous listening, background monitoring, or data access unless a supported permissioned service is active.
- Do not read private notifications, contacts, files, messages, or location without a clear feature purpose and explicit Android permission.
- Accessibility automation is opt-in, narrow in scope, and requires confirmation for consequential actions.
- Financial records are local-first, backed up only to user-approved destinations, and audit logged.
- Never invent customer details, GSTIN, invoice numbers, payment records, or signatures.
- Preserve the Radha Enterprises invoice PDF as the approved invoice layout reference; render and visually inspect before release.
- Never modify the GitHub main branch. Work only on android-clean-rebuild-v2 until review.

## Proposed architecture
### Android client
- Kotlin + Jetpack Compose UI.
- MVVM / repository pattern.
- Room database for offline-first structured records.
- DataStore for preferences and feature toggles.
- WorkManager for deferrable sync, backups, and scheduled housekeeping.
- Android SpeechRecognizer or an approved speech-to-text provider, started only by explicit user action.
- Foreground microphone service only during a user-started capture session, with RECORD_AUDIO permission and visible notification.
- NotificationListenerService only as an optional, separately enabled feature with source-app allowlist and local redaction.
- AccessibilityService only for explicitly enabled, user-triggered workflows; no hidden control or broad scraping.
- Android Sharesheet and Storage Access Framework for file import/export.

### Business core
- Customer master and address/GST profile.
- Item and HSN/SAC catalogue.
- Tax calculator with CGST/SGST/IGST rules, rounding tests, and place-of-supply validation.
- Separate sequential counters for estimates/proforma invoices and tax invoices.
- Payment ledger: invoice total, received amount, previous balance, current outstanding.
- PDF renderer using a fixed template engine with font embedding, measured text wrapping, cell padding, overflow detection, and PDF raster-preview tests.
- Immutable issued-document snapshot and audit trail.

### Cloud and dashboard
- Local-first operation; cloud sync is optional and disabled until the user connects an account.
- Proposed backend: authenticated API + PostgreSQL + object storage with row-level access controls.
- Web dashboard mirrors approved mobile records and document status.
- Google Drive backup through official user-authorized file picker/API; never store OAuth secrets in the repository.
- Encrypt sensitive local data and use TLS for network transport.

## Android 15 platform constraints
- Microphone access requires RECORD_AUDIO and is subject to while-in-use restrictions.
- A microphone foreground service cannot be started from the background in ordinary cases; start it while the app is visible and the user initiates capture.
- Android 15 prohibits starting microphone foreground services from BOOT_COMPLETED.
- Foreground services must show a user-visible notification and be used only for user-noticeable work.
- WorkManager is for deferrable background jobs, not continuous microphone capture.

## Delivery phases
### Phase 0 — Audit and baseline
- Inspect all existing project files and workflows on this branch.
- Record Gradle, Kotlin, SDK, package name, app permissions, current UI, and CI state.
- Confirm main is untouched.
- Build a clean baseline APK and record the workflow run and artifact before claiming success.

### Phase 1 — Silent foundation
- App shell, navigation, dark/light support, silent response setting.
- Local Room database and DataStore.
- Text command inbox and task capture.
- Exportable local backup and restore.

### Phase 2 — User-initiated voice input
- Push-to-talk control.
- Visible recording state and persistent notification.
- Speech-to-text transcript preview, edit, and submit.
- Stop/cancel controls; no auto-start on boot.

### Phase 3 — Business workspace
- Customers, products, HSN, tax calculator, payment ledger.
- Customer report import with validation.
- Separate invoice/proforma numbering with collision prevention.
- Radha Enterprises-style invoice renderer and PDF quality gate.

### Phase 4 — Mobile bridge
- Optional notification summaries from explicitly allowlisted apps.
- User-triggered, narrowly scoped accessibility workflows.
- Confirmation before sending messages, making payments, deleting, or changing account settings.

### Phase 5 — Cloud dashboard and integrations
- Authenticated sync and role-based access.
- User-authorized Drive backup.
- Dashboard, audit log, conflict resolution, and restore testing.

## Release quality gates
- Unit tests for tax arithmetic, rounding, numbering, balance calculations, and permissions.
- UI tests for silent mode and voice capture lifecycle.
- PDF regression tests: no text/border intersection, no clipping, correct font embedding, QR/signature presence, and exact page count.
- Offline tests and backup/restore test.
- CI build must pass; APK artifact must be downloadable and installation-tested before release status is declared.

## First implementation checkpoint
The branch was created from main on 2026-11-02. No APK build or installation is claimed by this architecture document. The next engineering action is a branch-only source/workflow audit, followed by a baseline build.
