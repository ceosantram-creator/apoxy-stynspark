# AURS ∞ Commerce — Secure Deployment Readiness (NOT LAUNCHED)

## Outcome / वर्तमान स्थिति
* Local code prepared for Docker hosting; no platform account or paid instance created.
* GitHub Pages public static website from `main` is a separate product. **Never deploy this FastAPI app on GitHub Pages**: it cannot run its database/API there.
* Keep this code in an isolated deployment branch. Avoid merging into `main` until separately reviewed.
* SQLite and uploaded promo images reside together under `AURS_DATA_DIR`; a disk mount is ESSENTIAL for durability. Single uvicorn worker is deliberate.

## Required host secrets / production refusal
1. `AURS_ENV=production` — production mode blocks startup unless all mandatory settings below are valid. For private staging only, explicitly set `AURS_STAGING_PREVIEW_ALLOW=1` and keep network access restricted.
2. `AURS_PUBLIC_ORIGIN=https://your-owned-https-domain.example` — no path; used for CSRF `Origin` check.
3. `AURS_COOKIE_SECURE=1` — HttpOnly, SameSite=strict admin session over HTTPS.
4. `AURS_ADMIN_PASSWORD` — unique 20+ character secret, never a sample.
5. `AURS_SECRET_KEY` — fresh random 64+ character secret; changing this invalidates sessions.
6. `AURS_DATA_DIR=/data` — absolute mounted persistent disk path, writable by UID 10001.
7. `AURS_TRUSTED_PROXY_IPS` — only known proxy IPs; default loopback. Never blindly trust forwarded headers from arbitrary client addresses.
8. `AURS_BACKUP_PASSPHRASE` — separate strong private value for encrypted manual backups; never same as admin secret.

### Railway draft (NOT activated)
* Create service from this subdirectory `commerce-mvp` only if and when approved; choose Dockerfile in that folder.
* Attach a Railway Volume mounted at `/data`, ensure UID 10001 has write access (provider-specific permissions may require adjustment).
* Keep `AURS_ENV=staging` with `AURS_STAGING_PREVIEW_ALLOW=1` and **no public routing** until authorized security verification, then separately approve production variables and domain. The Docker startup refuses an unapproved non-production bind.
* Configure environment secrets in Railway UI, NOT `.env` in Git.
* Verify backup export from `/data` and restore into a fresh empty offline test directory. Note Railway volume cannot be assumed to be a multi-replica or cross-region backup.
* Reference: https://docs.railway.com/volumes

### Render draft (NOT activated)
* Create a Docker web service from this subdirectory if approved.
* Paid persistent disk mounted at `/data`; only files under mount persist, and disk may affect zero-downtime deployment and scaling.
* Keep auto-deploy disabled and do not attach a production domain before approval.
* Reference: https://render.com/docs/disks

## Security/privacy gates BEFORE public launch
- [ ] Confirm verified legal owner/controller contact, grievance mechanism and retention schedule; review applicable Indian data-protection/consumer laws with counsel.
- [ ] Publish reviewed bilingual privacy notice (current `/privacy` page is **draft** and must NOT be treated as compliant policy).
- [ ] Hosting processor terms, access controls, region and administrator access ownership reviewed.
- [ ] TLS, restricted GitHub deployment permissions, login throttling at edge/WAF and network firewalls tested.
- [ ] Confirm CSP/security headers; inspect all client-side interpolation for XSS; supply `AURS_PUBLIC_ORIGIN` and test CSRF behind actual reverse proxy.
- [ ] Enable production logging that suppresses enquiry payload, tokens, raw phone numbers and full cookies.
- [ ] Set encrypted scheduled **off-host** backups; run recovery drill and verify SQLite `PRAGMA integrity_check`.
- [ ] Decide lead retention/deletion workflow; record manual data subject requests; linked orders require review before erasure.
- [ ] Replace fictional demo drafts with genuine approved media only. Never upload production vector/stone coordinate masters to promo gallery.
- [ ] Connect owned WhatsApp Business number and verify click-to-chat link; no automated WhatsApp messaging yet.
- [ ] Implement and sandbox-test signed Meta/WhatsApp webhooks before accepting live callbacks; app currently has NO webhook receiver or outbound sender.
- [ ] Obtain proper marketing consent/legal basis before adding Meta Pixel, CAPI and cross-platform identifiers; app currently sends NO tracking events.
- [ ] Explicit human approval for public publishing, campaign spending, final pricing, real order acceptance and any automated outreach.

## Config readiness API (private)
GET `/api/admin/integrations/readiness` after login returns ONLY boolean flags whether env values are set. This does NOT verify credentials or Meta authorization. No ad API actions, pixels, conversions, WhatsApp auto-messages or webhooks are implemented. All integrations are OFF.

## Manual acceptance / no spend
Campaign draft: SANTRAM Industries, 7 days, 300 INR/day, 2100 INR base excl. tax, 3 approved creatives, Tiruppur and Coimbatore, Engagement > Messaging Apps > WhatsApp. This is a **plan, not an ad**.

## How to test without exposing a site
```sh
python -m pip install -r requirements.txt
python -m pip install pytest httpx cryptography
pytest -q tests
# local only: the environment values are YOUR OWN secrets; never check them into Git
```

## Limitations (do not overstate)
This MVP is not production-cleared. In-memory login and enquiry rate-limit state resets on restarts and is per process; a production WAF/Redis distributed limiter is needed for higher volume. SQLite backups must run with care; encryption passphrase must be recoverable offline. Database encryption at rest is provided by the hosting provider/disk configuration, not the application. Current draft privacy page lacks verified company contact details. No credentials have been configured, no cloud hosting connected, no public release, no ad spend.
