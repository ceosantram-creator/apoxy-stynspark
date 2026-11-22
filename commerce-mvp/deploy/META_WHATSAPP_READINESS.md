# Meta Ads + WhatsApp Business Cloud — Configuration-only Readiness

## Scope: no live interaction
* Manual `/settings` WhatsApp number -> `wa.me` click-to-chat (existing). Not the WhatsApp Cloud API.
* Credentials are optional and NEVER serialized into browser HTML/JS or readiness JSON. Do not put API tokens in GitHub Secrets unless a future approved CI use genuinely requires them; prefer the hosting provider's runtime secret manager.
* Private readiness endpoint: `GET /api/admin/integrations/readiness` shows redacted booleans and hard-coded `connectors_live=false`.

## Meta: account permissions to verify later
- [ ] Business Manager ownership and ad account ID under account owner's control.
- [ ] Correct Facebook Page and Instagram account access, owned business WhatsApp number.
- [ ] Click-to-WhatsApp ads availability for intended region/account; local UI can vary.
- [ ] Marketing measurement legal basis, consent and event minimization reviewed before enabling Pixel/CAPI.
- [ ] Spending limit: manual 300 INR/day × 7 days before taxes; actual spend only after explicit approval.

## WhatsApp Cloud API: prerequisites, not enabled
- [ ] Business Account ID; Phone Number ID; approved access token scopes; own verified business number.
- [ ] Meta app secret, webhook verify token; HTTPS callback URL; HMAC-SHA256 verification of raw request bodies BEFORE processing.
- [ ] Subscribe only required webhook events; deduplicate message IDs and store minimal customer data.
- [ ] Approved templates, user opt-in policy, messaging-window rules, opt-out handling and operator override.
- [ ] Sandbox tests, failure retries, audit trail and message safety limits.

## Variables (store only on server)
`AURS_META_AD_ACCOUNT_ID`, `AURS_META_PIXEL_ID`, `AURS_META_CAPI_TOKEN`, `AURS_WA_PHONE_NUMBER_ID`, `AURS_WA_BUSINESS_ACCOUNT_ID`, `AURS_WA_ACCESS_TOKEN`, `AURS_WA_VERIFY_TOKEN`, `AURS_WA_APP_SECRET`.

Only presence flags are read. No Meta client exists in this code; setting a token cannot activate a paid ad, a pixel, a webhook or a WhatsApp message.

Official references:
https://developers.facebook.com/docs/graph-api/webhooks/getting-started/
https://developers.facebook.com/docs/whatsapp/cloud-api/
