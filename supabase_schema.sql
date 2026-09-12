-- Hackout26 P2P Energy Trading Marketplace
-- Supabase schema matching app/models/schemas.py

create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    owner_name text not null,
    block text not null,
    flat_no text not null,
    family_size int not null,
    has_solar_panels boolean not null default false,
    panel_capacity_kw numeric default 0,
    panel_brand text,
    net_metering_status text default 'Not Applicable',
    created_at timestamptz default now()
);

create table if not exists meter_readings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    date date not null,
    sunlight_hours numeric default 0,
    energy_produced_kwh numeric default 0,
    energy_consumed_kwh numeric default 0,
    excess_power_kwh numeric default 0,
    grid_import_kwh numeric default 0,
    created_at timestamptz default now(),
    unique (user_id, date)
);

create table if not exists listings (
    id uuid primary key default gen_random_uuid(),
    seller_id uuid references users(id) on delete cascade,
    seller_block text not null, -- denormalized from users.block for fast block filtering
    available_kwh numeric not null,
    price_per_kwh numeric not null,
    status text not null default 'open', -- open | matched | fulfilled | cancelled
    valid_until timestamptz,
    created_at timestamptz default now()
);

create table if not exists trades (
    id uuid primary key default gen_random_uuid(),
    listing_id uuid references listings(id),
    buyer_id uuid references users(id),
    seller_id uuid references users(id),
    energy_kwh numeric not null,
    price_per_kwh numeric not null,
    total_price numeric not null,
    status text not null default 'pending', -- pending | confirmed | completed | failed
    created_at timestamptz default now()
);

create table if not exists grid_status (
    id uuid primary key default gen_random_uuid(),
    block text unique not null,
    state text not null default 'normal', -- normal | outage | degraded
    note text,
    updated_at timestamptz default now()
);

-- Helpful indexes
create index if not exists idx_meter_readings_user_date on meter_readings(user_id, date);
create index if not exists idx_listings_status on listings(status);
create index if not exists idx_listings_block on listings(seller_block);
create index if not exists idx_trades_buyer on trades(buyer_id);
create index if not exists idx_trades_seller on trades(seller_id);
