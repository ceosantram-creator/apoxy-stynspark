-- AURS NEXT03: POSTGRES + RLS SECURITY BLUEPRINT ONLY.
-- NOT DEPLOYED, NOT FUNCTIONAL AS A COMPLETE BACKEND.
-- An engineer must review security, migration strategy, auth roles, policies
-- and run cross-tenant tests before applying to any hosted database.
-- Never include credentials or real customer data in a public GitHub repository.

begin;
create extension if not exists pgcrypto;

create table if not exists public.aurs_organizations (
  id uuid primary key default gen_random_uuid(),
  code text not null unique check (length(code) between 2 and 80),
  created_at timestamptz not null default now()
);

create table if not exists public.aurs_memberships (
  org_id uuid not null references public.aurs_organizations(id),
  user_id uuid not null references auth.users(id),
  role text not null check (role in ('owner','manager','designer','operator','viewer')),
  created_at timestamptz not null default now(),
  primary key (org_id,user_id)
);

create table if not exists public.aurs_projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.aurs_organizations(id),
  internal_alias text not null check (length(internal_alias) between 1 and 80),
  stage text not null default 'enquiry'
    check(stage in ('enquiry','design','costing','approval','production','dispatch','done')),
  approval_state text not null default 'pending'
    check(approval_state in ('pending','approved','rejected')),
  dispatch_state text not null default 'not-ready'
    check(dispatch_state in ('not-ready','ready','sent')),
  version int not null default 0 check (version >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id,org_id)
);

create table if not exists public.aurs_approval_requests (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.aurs_organizations(id),
  project_id uuid not null,
  requested_by uuid not null references auth.users(id),
  action_type text not null check(action_type in (
    'customer_quote','customer_message','production_release','dispatch_release',
    'payment','marketing_publish','public_launch','data_export')),
  state text not null default 'pending'
    check(state in ('pending','approved','rejected','expired','cancelled')),
  idempotency_key uuid not null,
  created_at timestamptz not null default now(),
  expires_at timestamptz,
  unique(org_id,idempotency_key),
  foreign key(project_id,org_id) references public.aurs_projects(id,org_id)
);

create table if not exists public.aurs_approval_events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.aurs_organizations(id),
  request_id uuid not null references public.aurs_approval_requests(id),
  actor_id uuid not null references auth.users(id),
  event_type text not null
    check(event_type in ('requested','approved','rejected','expired','cancelled','executed','failed')),
  evidence_digest text,
  recorded_at timestamptz not null default now(),
  safe_metadata jsonb not null default '{}'::jsonb
);

create table if not exists public.aurs_audit_events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.aurs_organizations(id),
  actor_id uuid references auth.users(id),
  event_type text not null,
  target_table text not null,
  target_id uuid,
  recorded_at timestamptz not null default now(),
  safe_metadata jsonb not null default '{}'::jsonb
);

-- No client writes to approval, audit or critical project state. Real writes
-- require a separately implemented, tested authorization service or RPC.
revoke all on public.aurs_organizations, public.aurs_memberships,
  public.aurs_projects, public.aurs_approval_requests,
  public.aurs_approval_events, public.aurs_audit_events
  from anon, authenticated;
grant select on public.aurs_memberships, public.aurs_organizations,
  public.aurs_projects, public.aurs_approval_requests,
  public.aurs_approval_events, public.aurs_audit_events to authenticated;

alter table public.aurs_organizations enable row level security;
alter table public.aurs_memberships enable row level security;
alter table public.aurs_projects enable row level security;
alter table public.aurs_approval_requests enable row level security;
alter table public.aurs_approval_events enable row level security;
alter table public.aurs_audit_events enable row level security;

-- A user can read their own memberships, not other users' membership lists.
create policy aurs_membership_self_read on public.aurs_memberships
  for select to authenticated using(user_id=auth.uid());

create policy aurs_org_member_read on public.aurs_organizations
  for select to authenticated
  using(exists(select 1 from public.aurs_memberships m
    where m.org_id=id and m.user_id=auth.uid()));

create policy aurs_project_member_read on public.aurs_projects
  for select to authenticated
  using(exists(select 1 from public.aurs_memberships m
    where m.org_id=org_id and m.user_id=auth.uid()));

create policy aurs_approval_request_member_read on public.aurs_approval_requests
  for select to authenticated
  using(exists(select 1 from public.aurs_memberships m
    where m.org_id=org_id and m.user_id=auth.uid()));

create policy aurs_approval_event_member_read on public.aurs_approval_events
  for select to authenticated
  using(exists(select 1 from public.aurs_memberships m
    where m.org_id=org_id and m.user_id=auth.uid()));

create policy aurs_audit_event_member_read on public.aurs_audit_events
  for select to authenticated
  using(exists(select 1 from public.aurs_memberships m
    where m.org_id=org_id and m.user_id=auth.uid()));

-- Event rows cannot be modified via normal UPDATE/DELETE, even by privileged
-- application roles. DB owners can change schemas, so this is not absolute
-- tamper protection: independently protected external backups/log sinks remain necessary.
create or replace function public.aurs_reject_event_rewrite()
returns trigger
language plpgsql
as $$
begin
  raise exception 'AURS event rows are append-only';
end $$;

create trigger aurs_approval_events_no_rewrite
  before update or delete on public.aurs_approval_events
  for each row execute function public.aurs_reject_event_rewrite();

create trigger aurs_audit_events_no_rewrite
  before update or delete on public.aurs_audit_events
  for each row execute function public.aurs_reject_event_rewrite();

commit;

-- NOT INCLUDED / REQUIRED BEFORE DEPLOYMENT:
-- 1. Identity invitation + MFA policy and organization onboarding.
-- 2. SECURITY DEFINER approval RPC with fixed search_path; verified auth.uid(),
--    actor role, project-org consistency, transition checks, evidence,
--    request expiry, optimistic concurrency, transaction + idempotency checks.
-- 3. Server-only action executor; never expose service-role key to frontend.
-- 4. Database/Storage least privilege and full adversarial RLS tests.
-- 5. Protected backups, tested restore, data retention, deletion process.
-- 6. Versioned migration procedures; rerunning CREATE POLICY/TRIGGER fails
--    unless managed with a migration tool.
