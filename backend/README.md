# SANTRAM AI INFINITY — Self-hosted backend

## Security model
- The OpenAI API key exists only in the backend process environment. Never put it in Android source, APK resources, GitHub files, or client preferences.
- Android authenticates with a separate high-entropy `SANTRAM_APP_TOKEN`; use HTTPS in production.
- Helmet headers, JSON body limits, per-IP rate limiting, timing-safe bearer comparison, input validation, and generic provider errors are enabled.
- Keep `.env` out of Git. Rotate the app token if a device is lost. Put the service behind a TLS reverse proxy and firewall; do not expose port 8080 directly to the public internet.
- Add per-user identity, persistent audit records, tenant isolation, and usage/budget enforcement before multi-device or commercial deployment.

## Deploy on your server
1. Install Docker Engine and Docker Compose.
2. Copy `.env.example` to `.env` on the server only.
3. Set `OPENAI_API_KEY` to the key from your OpenAI API project, and set a long random `SANTRAM_APP_TOKEN`.
4. Run `docker compose up -d --build`.
5. Configure a TLS reverse proxy for the domain and forward to `127.0.0.1:8080`.
6. Verify `GET /health` and then configure the Android app with the HTTPS base URL and app token.

## API
`POST /v1/chat` with `Authorization: Bearer <SANTRAM_APP_TOKEN>` and JSON:
```json
{"messages":[{"role":"user","content":"Namaste SANTRAM AI"}]}
```
Response: `{"reply":"...","model":"..."}`.

The server does not implement phone, WhatsApp, GST filing, production-machine control, or cloud backup actions. Those require separate Android permissions, provider integrations, user confirmation, and audited action adapters.
