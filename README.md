# APOXY GLOBAL TRADE — Free-first B2B workspace

Public website: https://ceosantram-creator.github.io/apoxy-stynspark/

This is a deployed static Progressive Web App (PWA) and browser-local business workspace for early-stage global B2B operations. It includes:
- Creation Studio for technical design briefs and size/DPI calculations.
- Buyer lead CRM with country, contact, requirement, source, status and follow-up.
- Supplier directory with manually entered verification status.
- Multi-currency quotation estimate (INR, USD, EUR, GBP, AED, ZAR, AUD, CAD).
- Order register with payment and production status.
- Follow-up task list.
- RFQ draft workflow, project records, production checklist and manual shipment log.
- JSON backup and restore for both the original workspace and Global Trade Desk.

## Start using it
1. Open the public website in Chrome.
2. On Android Chrome, use menu → Add to Home screen / Install app if offered.
3. Open Global Trade Desk.
4. Add real buyer and supplier records; never mark a party verified without checks.
5. Export a JSON backup regularly and keep a copy in Google Drive.

## Data storage and important limits
- This is a static GitHub Pages deployment. All CRM records currently remain in local browser storage on the device/browser that entered them.
- There is no shared cloud database, cross-device sync, team login, admin panel or role-based access.
- RFQs and quotes are drafts/estimates only. The app does not send email/WhatsApp messages or transmit RFQs to companies.
- Supplier and buyer verification is manual. No lead is confirmed to be a buyer merely because a public company exists.
- Quote estimates use the selected currency consistently but do not fetch live FX rates. They exclude taxes, customs duties, FX conversion, payment/bank fees, insurance and costs not entered. Validate all landed costs before quoting.
- Order, payment, production and shipment statuses are records entered by the user; no payment, purchase order, courier booking or tracking API is connected.
- The Ask APOXY assistant is a local workflow router, not a connected ChatGPT/LLM. No AI API key is embedded.
- Creation Studio creates a technical brief, not finished PNG/SVG/PDF artwork.
- Do not store passwords, bank/card details, API keys or other secrets in the app. Export backups securely; JSON backups contain your business contacts.

## What is needed for true multi-user cloud production
1. Managed authentication, database, row-level security and tenant separation (e.g. Supabase or Firebase project owned by the business).
2. Server-side functions for email/WhatsApp, AI, payment webhooks and permissions; secrets must never be placed in browser code.
3. Consent, privacy policy, data retention, backup and deletion controls.
4. Real supplier onboarding, GST/company checks, sample QC, contracts and buyer qualification.
5. Payment provider and shipping integrations tested in sandbox, then approved for production.
6. Monitoring, error reporting, rate limits and automated tests.

Free static hosting is live, but it is not a free hosted SaaS backend. Do not use this prototype as proof of counterparty verification or as the sole record for money-moving transactions.
