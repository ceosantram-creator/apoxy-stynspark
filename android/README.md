# SANTRAM PERSONAL AI INFINITY — Android foundation

This is an isolated Android 15 app module under `android/`; the existing browser prototype at the repository root is preserved.

## Current scope
- Kotlin + Jetpack Compose.
- Text-only command inbox (in-memory prototype state).
- Silent mode presentation.
- No microphone, notification listener, accessibility, contacts, SMS, or location permissions.
- No cloud connection or external actions.

## Build
Open this `android/` directory in Android Studio with JDK 17 and Android SDK Platform 35, or run:
`gradle assembleDebug`

The APK output, after a successful build, is:
`android/app/build/outputs/apk/debug/app-debug.apk`

## Next
1. Add Room persistence and DataStore preferences.
2. Add user-started push-to-talk with visible recording state and foreground notification.
3. Add customer, item, tax, payment, and invoice modules with PDF regression tests.
4. Add opt-in integrations only after explicit permission and security review.
