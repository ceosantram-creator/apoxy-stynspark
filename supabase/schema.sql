-- APOXY GLOBAL TRADE: Supabase starter schema
-- Run once in Supabase SQL Editor. Uses authenticated users + organization-scoped RLS.
create extension if not exists pgcrypto;

create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default now()
);
create table if not exists public.organization_members (
  organization_id uuid not null references public.organizations(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner','admin','member')),
  created_at timestamptz not null default now(),
  primary key (organization_id,user_id)
);

create or replace function public.is_org_member(org uuid)
returns boolean language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.organization_members m where m.organization_id=org and m.user_id=auth.uid()) $$;
create or replace function public.has_org_role(org uuid, allowed text[])
returns boolean language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.organization_members m where m.organization_id=org and m.user_id=auth.uid() and m.role = any(allowed)) $$;

create or replace function public.create_apoxy_workspace(workspace_name text)
returns uuid language plpgsql security definer set search_path = public
as $$
declare new_id uuid;
begin
  if auth.uid() is null then raise exception 'Authentication required'; end if;
  if length(trim(coalesce(workspace_name,''))) < 2 then raise exception 'Workspace name is required'; end if;
  insert into public.organizations(name,created_by) values (trim(workspace_name),auth.uid()) returning id into new_id;
  insert into public.organization_members(organization_id,user_id,role) values (new_id,auth.uid(),'owner');
  return new_id;
end;
$$;

create table if not exists public.buyer_leads (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 company_name text not null, country text, contact_name text, email text, phone text, product_need text, quantity text,
 target_price text, lead_source text, status text not null default 'New', follow_up_on date, notes text,
 created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.suppliers (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 company_name text not null, location text, contact_name text, email text, phone text, capability text, moq text, indicative_cost numeric,
 verification_status text not null default 'Unverified', notes text,
 created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.rfqs (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 rfq_number text, product text not null, specification text, quantity numeric, target_price numeric, currency text not null default 'INR',
 destination_country text, required_by date, status text not null default 'Draft', created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.quotes (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 rfq_id uuid references public.rfqs(id) on delete set null, buyer_name text, supplier_name text, product text not null,
 quantity numeric, currency text not null default 'INR', unit_cost numeric, freight numeric default 0, other_costs numeric default 0,
 selling_total numeric, gross_margin numeric, validity_date date, status text not null default 'Draft',
 created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.trade_orders (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 po_number text not null, buyer_name text, supplier_name text, product text not null, quantity numeric, currency text not null default 'INR',
 order_value numeric, payment_status text not null default 'Pending', production_status text not null default 'Not started',
 due_date date, notes text, created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.follow_up_tasks (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.organizations(id) on delete cascade,
 title text not null, company text, due_on date, priority text not null default 'Normal', completed boolean not null default false,
 notes text, assigned_to uuid references auth.users(id), created_by uuid not null default auth.uid() references auth.users(id), created_at timestamptz not null default now()
);

alter table public.organizations enable row level security;
alter table public.organization_members enable row level security;
create policy "members can view own organizations" on public.organizations for select using (public.is_org_member(id));
create policy "owners and admins update organization" on public.organizations for update using (public.has_org_role(id,array['owner','admin'])) with check (public.has_org_role(id,array['owner','admin']));
create policy "members view membership" on public.organization_members for select using (public.is_org_member(organization_id));
create policy "owners manage membership" on public.organization_members for all using (public.has_org_role(organization_id,array['owner'])) with check (public.has_org_role(organization_id,array['owner']));

do $$
declare t text;
begin
 foreach t in array array['buyer_leads','suppliers','rfqs','quotes','trade_orders','follow_up_tasks'] loop
  execute format('alter table public.%I enable row level security',t);
  execute format('create policy "org members read %1$I" on public.%1$I for select using (public.is_org_member(organization_id))',t);
  execute format('create policy "org members insert %1$I" on public.%1$I for insert with check (public.is_org_member(organization_id) and created_by = auth.uid())',t);
  execute format('create policy "org members update %1$I" on public.%1$I for update using (public.is_org_member(organization_id)) with check (public.is_org_member(organization_id))',t);
  execute format('create policy "org admins delete %1$I" on public.%1$I for delete using (public.has_org_role(organization_id,array[''owner'',''admin'']))',t);
 end loop;
end $$;

grant usage on schema public to authenticated;
grant select,insert,update,delete on public.organizations, public.organization_members, public.buyer_leads, public.suppliers, public.rfqs, public.quotes, public.trade_orders, public.follow_up_tasks to authenticated;
grant execute on function public.create_apoxy_workspace(text) to authenticated;
grant execute on function public.is_org_member(uuid) to authenticated;
grant execute on function public.has_org_role(uuid,text[]) to authenticated;
