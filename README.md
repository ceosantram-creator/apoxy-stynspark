# SANTRAM INDUSTRIES — AI Operating System INFINITY

Android 15 local-first operating system foundation for personal and business workflows.

## Current Android checkpoint

The Android app now includes:
- Central dashboard with task, customer and invoice-draft counts.
- Personal command inbox with locally persisted tasks and completion status.
- Business customer register (name, phone, optional GSTIN).
- Internal invoice draft register (customer, description, amount).
- Silent Mode preference (silent by default).
- User-selected JSON backup export and restore through Android's document picker.
- No microphone, notification-listener, accessibility or location permission is requested by this foundation.

## Build

The Android project is under `android/`. CI uses JDK 17 and Gradle 8.9:

```bash
cd android
gradle assembleDebug
```

The branch-only GitHub Actions workflow builds a debug APK on pushes to `android-clean-rebuild-v2`.

## Important release limitations

This checkpoint is an offline-first functional foundation, **not yet the complete AI Operating System or a production financial system**:
- Tasks, customers and invoice drafts are stored locally in app preferences. They are not encrypted with a dedicated database/key-management layer yet.
- Backup export/restore is user initiated. Cloud sync and Google Drive integration are not connected.
- Invoice records are drafts only. GST calculations, compliant numbering, PDF generation, e-invoice/e-way bill, payment reconciliation and audit-grade immutable issue snapshots are not implemented.
- No AI model/provider is connected. No automatic task/date extraction or autonomous agent execution is claimed.
- Voice capture, reminders/alarms, background services, WhatsApp/Gmail/Drive connectors and notification summaries are not implemented in this checkpoint.
- Do not enter sensitive credentials or payment secrets. Validate backups and keep them in a private location.

## Required production roadmap

1. Room database, migrations, encrypted local storage and automated backup/restore tests.
2. User-initiated speech-to-text with clear microphone permission, recording state and visible controls.
3. Reliable reminder scheduling with Android notification permission and exact-alarm policy handling.
4. Business catalogue, tax rules, validated invoice numbering, PDF renderer and regression tests.
5. AI provider adapter with server-side secrets, consent, usage limits and human approval for consequential actions.
6. Authenticated cloud sync, conflict handling, audit log and user-authorized Drive integration.
7. Optional narrow notification/accessibility bridges, individually enabled and permissioned.
8. Release signing, device installation tests, privacy review and recovery testing.

## Protected development boundary

All Android development remains on `android-clean-rebuild-v2`. The `main` branch is protected from this work until explicit review.
