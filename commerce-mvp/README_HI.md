# DEPLOYMENT PREPARATION V02 — NOT LIVE

For safe deployment guidance read `deploy/READINESS_HI.md`. The current code has **no Meta/WhatsApp live connectors, no ad spend, no public launch**. GitHub Pages cannot host this API.

# AURS ∞ Commerce Network — WORKING MVP (2026-11-23)

A multilingual, responsive **FastAPI + SQLite** web application for **SANTRAM INDUSTRIES**, **STYNSPARK** and **AURS**, with a separate public brand experience and password-protected owner dashboard. This is a **working local/server MVP, not a published website**.

## Features actually implemented

- Public homepage and branded routes (`/brand/santram`, `/brand/stynspark`, `/brand/aurs`)
- Product listing / individual pages restricted to **approved AND published** concepts
- Admin uploads **promotional artwork only**; changing an image forces `pending` and unpublishes the product
- Lead and bulk-enquiry intake with consent checkbox and basic rate limiting
- Admin lead status; CSV export; draft order → approval → production → ready → dispatched lifecycle
- Adjustable material/labour/wastage/shipping/GST/margin quotation calculator, no auto public pricing
- WhatsApp Business contact link after admin adds a number with country code
- Planned Meta Ads campaign (Tiruppur and Coimbatore; ₹300/day for 7 days; 3 approved designs); explicitly **not launched**
- Hindi/English toggle and mobile-first screens
- Anonymous pageview totals, without IP analytics or tracking pixels
- SQLite persistent records; signed HttpOnly session cookies; no default admin password
- Programmatic product template supports many products using **one** application, not 1,000 domains

## Run locally

Requirements: Python 3.11+.

```bash
cd AURS_Commerce_MVP
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export AURS_ADMIN_PASSWORD='YOUR-UNIQUE-PASSWORD-OF-AT-LEAST-12-CHARS'
export AURS_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_hex(32))')"
export AURS_COOKIE_SECURE=0  # local HTTP only
uvicorn app:app --host 127.0.0.1 --port 8000
```

Visit `http://127.0.0.1:8000` for the public site, `http://127.0.0.1:8000/admin` for private dashboard. On Android, use an authorized HTTPS deployment; `127.0.0.1` on phone does **not** point at your laptop.

**Protect secret values**. Do not commit them. Use a proper HTTPS reverse proxy for internet publishing and set `AURS_COOKIE_SECURE=1`. Configure persistent database storage, encrypted backups, domain, privacy notice, spam prevention, monitoring and compliance review. SQLite is suitable for the small MVP; consider managed PostgreSQL and robust role-based authorization as the business scales.

## 3 sample design records

Database initially contains three **PENDING fictional demo concept records**, not your real uploaded artwork. Nothing is public until you upload an authorized promotional preview and explicitly `Approve & Publish`. Do not publish placeholders as if they are actual products. No original technical design masters are included.

## What has NOT been connected

**Live Meta Ads, Appier, Appy Pie, Meta Pixel, Meta Conversions API, WhatsApp Business Cloud API, payment gateways, Instagram, SMS/email automation, external CRM, and external order/shipping providers**. This MVP contains only a **manual** Ads plan and configurable WhatsApp click-to-chat link. Actual ad spend must never occur from this MVP without separate authorized account connection and specific approval.

## Publishing checklist

1. Confirm domain ownership, hosting tier and production HTTPS.
2. Set long `AURS_ADMIN_PASSWORD`, random `AURS_SECRET_KEY`, and `AURS_COOKIE_SECURE=1` through your hosting service's secret manager.
3. Attach **persistent** database/image storage and scheduled encrypted backups; test restoring it.
4. Replace all sample records with original, legally cleared, customer-approved public artworks.
5. Set owned WhatsApp Business number through admin Settings and test `wa.me`.
6. Publish privacy / returns / terms / contact pages as applicable; ensure consent and Indian data protection compliance.
7. Test lead form, login/logout, image privacy, and approval gate; enable production logs and spam control.
8. Connect Meta Business, Instagram, Pixel/Conversions API only when authorized and after consent/legal review; **never place Meta CAPI tokens in browser JavaScript**.
9. Configure business email and reliable lead notifications; appoint the human who approves quotes, designs, advertising spend and orders.
10. Review traffic/load tests before expanding to 200–1,000 products; separate database and image/CDN hosting for scale.

## Indicative hosting costs; verify at checkout

- Railway Hobby: from US$5/month base incl. US$5 usage; usage above included amount and storage can add cost (https://docs.railway.com/pricing).
- Render starter web service: from US$7/month; managed Postgres, persistent disk, bandwidth extra (https://render.com/pricing).
- Appy Pie hosted site builder: marketing pages list US$0 free / US$36 per month / US$60 per month (US market, cited September 2026; Indian billing and e-commerce features vary) https://www.appypie.com/ai-website-builder.
- Domain, managed database, email, backups, media storage and Meta Ads are extra; do not treat base hosting as all-in production cost.

**Do not upload this code to a public web server without completing the security, privacy and durability launch checks.**
