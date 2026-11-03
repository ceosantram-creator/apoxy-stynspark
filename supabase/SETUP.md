# APOXY Global Trade — connect the cloud backend

The static website is deployed separately. This schema adds the database foundation for shared, multi-user records; it does not connect the website automatically.

## Setup (free-tier start)
1. Create a Supabase project in an account controlled by SANTRAM INDUSTRIES.
2. Open **SQL Editor → New query**.
3. Paste and run `supabase/schema.sql` from this repository.
4. In **Authentication → Providers**, enable Email (password or magic-link) and configure the allowed site URL:
   `https://ceosantram-creator.github.io`
   Add the full website URL to the redirect allow-list if Supabase requests it:
   `https://ceosantram-creator.github.io/apoxy-stynspark/`
5. Copy the Project URL and the publishable/anon key from the project's API settings. These are intended for browser clients when Row Level Security is enabled.
6. Send only the Project URL and publishable/anon key in this chat so the frontend can be wired to your project.

## Security rules
- Never share a Supabase database password, service_role key, secret API key, recovery code, or personal login password.
- Do not disable Row Level Security.
- The schema isolates records by organization membership. The workspace creator becomes its owner.
- Create a workspace by calling `create_apoxy_workspace('SANTRAM INDUSTRIES')` after signing in.
- The browser client must use only the publishable/anon key. All privileged actions belong in server-side functions.

## What this does and does not do
This schema creates organization membership, buyer leads, suppliers, RFQs, quotes, trade orders and follow-up tasks. It does not yet connect the website forms, email/WhatsApp delivery, AI model, payment provider, customs, courier tracking, KYC/GST verification or live foreign-exchange rates. Those require separate integrations and testing.

## First production test
Use two separate test user accounts. Create one workspace with account A, add sample records, then sign in as account B without membership and confirm that account B cannot read those records. Do not onboard real customers until this isolation test passes and backups/privacy controls are reviewed.
