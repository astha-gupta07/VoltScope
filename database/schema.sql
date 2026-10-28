-- ==============================================================================
-- VoltScope Database Schema (SQLite)
-- Schema DDL for Electric Vehicle Market Performance & Insights
-- Designed with strict data integrity: facts are separated by authentic grains.
-- ==============================================================================

-- 1. Data Provenance & Source Metadata
CREATE TABLE IF NOT EXISTS dataset_sources (
    source_key TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    publisher TEXT NOT NULL,
    source_url TEXT NOT NULL,
    license TEXT NOT NULL,
    retrieval_date TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    description TEXT
);

-- 2. Fact Table: Market-level EV Sales & Registrations
-- Grain: One row per geographical Area, Month (Date), and Drivetrain
CREATE TABLE IF NOT EXISTS fact_ev_sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    iso_3_code TEXT,
    area_type TEXT NOT NULL,             -- 'Country or economy' or 'Region'
    is_country BOOLEAN NOT NULL,         -- TRUE for sovereign countries, FALSE for supranational aggregates
    date TEXT NOT NULL,                  -- ISO-8601 YYYY-MM-01
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    data_frequency TEXT DEFAULT 'Monthly',
    drivetrain TEXT NOT NULL,            -- 'Battery electric', 'Plug-in hybrid', 'Hybrid', 'Petrol', etc.
    is_aggregate_drivetrain BOOLEAN NOT NULL, -- TRUE for 'Electric vehicle (BEV+PHEV)' & 'All drivetrains'
    registrations REAL,
    registrations_yoy_change REAL,
    registrations_yoy_change_pct REAL,
    share_of_registrations_pct REAL,
    ytd_registrations REAL,
    ytd_share_pct REAL,
    rolling_12m_registrations REAL,
    rolling_12m_share_pct REAL,
    continent TEXT,
    ember_region TEXT,
    is_eu_member BOOLEAN DEFAULT 0,
    is_oecd_member BOOLEAN DEFAULT 0,
    is_g20_member BOOLEAN DEFAULT 0,
    is_g7_member BOOLEAN DEFAULT 0,
    is_asean_member BOOLEAN DEFAULT 0,
    UNIQUE(area, date, drivetrain)
);

-- 3. Fact Table: National & Regional EV Fleet & Sustainability Impact
-- Grain: One row per geographical Area (Latest cumulative snapshot)
CREATE TABLE IF NOT EXISTS fact_fleet_impact (
    impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL UNIQUE,
    iso_3_code TEXT,
    area_type TEXT NOT NULL,
    is_country BOOLEAN NOT NULL,
    latest_available_date TEXT NOT NULL,
    ev_fleet_vehicles REAL NOT NULL,
    electricity_demand_gwh_yr REAL,
    oil_displaced_kbd_yr REAL,           -- Thousand barrels of oil equivalent per year
    oil_displaced_usd_million_yr REAL,   -- Economic value of displaced oil
    brent_price_usd REAL
);

-- 4. Dimension Table: Electric Vehicle Model Technical Specifications
-- Grain: One row per vehicle model generation
CREATE TABLE IF NOT EXISTS dim_vehicle_specs (
    model_id TEXT PRIMARY KEY,           -- Unique model slug
    brand TEXT NOT NULL,
    model_name TEXT NOT NULL,
    generation TEXT,
    body_category TEXT NOT NULL,         -- 'SUV / Crossover', 'Sedan', 'Hatchback', etc.
    raw_body_style TEXT,
    fuel_type TEXT NOT NULL,
    drivetrain_class TEXT NOT NULL,      -- 'Pure BEV' or 'Plug-in Hybrid / Multi-fuel'
    release_year INTEGER,
    power_hp REAL,
    battery_capacity_kwh REAL,
    range_wltp_km REAL,
    efficiency_km_per_kwh REAL,          -- Derived: range_wltp_km / battery_capacity_kwh
    consumption_kwh_100km REAL,
    fast_charge_dc_kw REAL,
    has_fast_charging BOOLEAN DEFAULT 0,
    towing_capacity_kg REAL,
    cargo_volume_liters REAL,
    seats INTEGER,
    doors INTEGER
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_sales_area_date ON fact_ev_sales (area, date);
CREATE INDEX IF NOT EXISTS idx_sales_year ON fact_ev_sales (year);
CREATE INDEX IF NOT EXISTS idx_sales_drivetrain ON fact_ev_sales (drivetrain);
CREATE INDEX IF NOT EXISTS idx_sales_is_country ON fact_ev_sales (is_country);
CREATE INDEX IF NOT EXISTS idx_sales_is_aggregate ON fact_ev_sales (is_aggregate_drivetrain);

CREATE INDEX IF NOT EXISTS idx_specs_brand ON dim_vehicle_specs (brand);
CREATE INDEX IF NOT EXISTS idx_specs_category ON dim_vehicle_specs (body_category);
CREATE INDEX IF NOT EXISTS idx_specs_drivetrain_class ON dim_vehicle_specs (drivetrain_class);
