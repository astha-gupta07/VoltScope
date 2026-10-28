-- ==============================================================================
-- VoltScope Analytical Views (SQLite)
-- Pre-aggregated, validated views tailored for Tableau extracts and BI reports.
-- ==============================================================================

-- 1. Annual EV Sales by Country (BEV + PHEV)
-- Excludes multi-country regions to prevent double-counting.
CREATE VIEW IF NOT EXISTS v_annual_ev_sales_by_country AS
SELECT 
    area AS country,
    iso_3_code,
    continent,
    year,
    SUM(registrations) AS total_ev_registrations,
    AVG(share_of_registrations_pct) AS avg_ev_market_share_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND drivetrain = 'Electric vehicle (BEV+PHEV)'
  AND is_aggregate_drivetrain = 1
GROUP BY area, iso_3_code, continent, year;

-- 2. Global EV Sales Trajectory Over Time
-- Uses the official 'World' aggregate row reported by Ember.
CREATE VIEW IF NOT EXISTS v_ev_sales_trend_global AS
SELECT 
    date,
    year,
    month,
    drivetrain,
    registrations AS global_registrations,
    registrations_yoy_change_pct AS yoy_growth_pct,
    share_of_registrations_pct AS global_ev_share_pct,
    rolling_12m_registrations
FROM fact_ev_sales
WHERE area = 'World'
  AND drivetrain IN ('Electric vehicle (BEV+PHEV)', 'Battery electric', 'Plug-in hybrid')
ORDER BY date ASC;

-- 3. Drivetrain Mix Transformation by Year (Global & Major Regions)
-- Compares market share of BEV, PHEV, Hybrid, Petrol, and Diesel cars over time.
CREATE VIEW IF NOT EXISTS v_drivetrain_mix_by_year AS
SELECT 
    year,
    drivetrain,
    SUM(registrations) AS total_registrations,
    ROUND(AVG(share_of_registrations_pct), 2) AS avg_share_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND is_aggregate_drivetrain = 0
  AND drivetrain IN ('Battery electric', 'Plug-in hybrid', 'Hybrid', 'Petrol', 'Diesel')
GROUP BY year, drivetrain;

-- 4. Vehicle Specifications Benchmarking by Body Category
-- Analyzes battery capacity, WLTP range, DC charging rate, and efficiency.
CREATE VIEW IF NOT EXISTS v_vehicle_specs_by_category AS
SELECT 
    body_category,
    COUNT(*) AS total_models,
    ROUND(AVG(battery_capacity_kwh), 1) AS avg_battery_kwh,
    ROUND(MIN(battery_capacity_kwh), 1) AS min_battery_kwh,
    ROUND(MAX(battery_capacity_kwh), 1) AS max_battery_kwh,
    ROUND(AVG(range_wltp_km), 1) AS avg_range_km,
    ROUND(MIN(range_wltp_km), 1) AS min_range_km,
    ROUND(MAX(range_wltp_km), 1) AS max_range_km,
    ROUND(AVG(fast_charge_dc_kw), 1) AS avg_fast_charge_dc_kw,
    ROUND(AVG(efficiency_km_per_kwh), 2) AS avg_efficiency_km_per_kwh,
    ROUND(AVG(consumption_kwh_100km), 1) AS avg_consumption_kwh_100km
FROM dim_vehicle_specs
WHERE battery_capacity_kwh > 0 
  AND range_wltp_km > 0
GROUP BY body_category;

-- 5. Fleet Sustainability & Environmental Impact Summary
-- Ranks nations by petroleum displacement and electricity demand.
CREATE VIEW IF NOT EXISTS v_fleet_sustainability_summary AS
SELECT 
    area AS country,
    iso_3_code,
    latest_available_date,
    ev_fleet_vehicles,
    electricity_demand_gwh_yr,
    oil_displaced_kbd_yr,
    oil_displaced_usd_million_yr,
    brent_price_usd,
    ROUND(oil_displaced_kbd_yr * 1000.0 / NULLIF(ev_fleet_vehicles, 0), 2) AS barrels_displaced_per_ev_yr
FROM fact_fleet_impact
WHERE is_country = 1
ORDER BY oil_displaced_kbd_yr DESC;

-- 6. Top EV Markets in Most Recent Full Calendar Year (2025)
CREATE VIEW IF NOT EXISTS v_top_ev_markets_latest_year AS
SELECT 
    area AS country,
    iso_3_code,
    continent,
    year,
    SUM(registrations) AS annual_ev_sales,
    ROUND(AVG(share_of_registrations_pct), 2) AS avg_market_share_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND year = 2025
  AND drivetrain = 'Electric vehicle (BEV+PHEV)'
GROUP BY area, iso_3_code, continent, year
ORDER BY annual_ev_sales DESC;
