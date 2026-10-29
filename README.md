# APOXY × STYNSPARK CREATION — Local-first MVP

A browser-based prototype implementing a responsive workspace, dynamic DTF design intake, dimension calculator, local project persistence, demo supplier matching, local RFQ drafts, production checklist, manual shipment records, subscription status placeholder, and JSON import/export.

## Run locally

Because this is a static PWA, you can open `index.html` directly for most features. For service-worker/offline testing, run a local static server from this directory, for example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

No package installation or dedicated server is required for this prototype. A local static server is only for development/testing. Static hosting can serve the app when you publish it.

## Data and limitations

- Projects, RFQs, shipment records and checklist selections are stored in browser `localStorage`.
- Export a JSON backup regularly. Clearing browser storage can erase the data.
- Supplier entries are fictional demo data, not verified suppliers.
- RFQs and shipment records are local drafts; nothing is sent to a supplier or courier.
- Subscription is a demo display only. There is no real authentication, payment processing, entitlement enforcement or admin identity.
- No AI provider is connected. Ask APOXY routes prompts into local workflows; it does not call an LLM.
- No production artwork is generated. Creation Studio creates a technical brief only. The preview is illustrative.
- SVG/PDF export, real vectorization, CMYK profile conversion, payment APIs, supplier APIs and courier APIs are not implemented.
- Do not store secrets, passwords, payment credentials or sensitive personal data in this prototype.

## Next production steps

1. Add automated tests and stronger schema validation.
2. Add managed authentication and tenant isolation.
3. Add a serverless entitlement verification endpoint and payment webhooks.
4. Add an AI provider adapter with server-side secret storage and usage limits.
5. Add real supplier records only after verification and consent.
6. Add provider-specific artwork export and preflight tools.
7. Integrate payment/logistics providers only after sandbox tests and contract review.
