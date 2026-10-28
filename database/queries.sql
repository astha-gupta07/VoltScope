-- ==============================================================================
-- VoltScope SQL Analytical Query Portfolio
-- Demonstrates core and advanced SQL syntax answering key business questions.
-- All queries are executable against database/voltscope.db.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Basic SELECT, WHERE, ORDER BY, LIMIT
-- Business Question: What are the top 10 individual monthly EV registration spikes in history?
-- ------------------------------------------------------------------------------
SELECT 
    area,
    date,
    drivetrain,
    registrations,
    share_of_registrations_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND drivetrain = 'Electric vehicle (BEV+PHEV)'
  AND registrations IS NOT NULL
ORDER BY registrations DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 2: GROUP BY and Aggregate Functions (SUM, AVG, COUNT, MIN, MAX)
-- Business Question: What are the total EV sales and average market share by continent?
-- ------------------------------------------------------------------------------
SELECT 
    continent,
    COUNT(DISTINCT area) AS total_countries,
    ROUND(SUM(registrations), 0) AS total_ev_registrations,
    ROUND(AVG(share_of_registrations_pct), 2) AS mean_monthly_market_share_pct,
    ROUND(MAX(share_of_registrations_pct), 2) AS peak_monthly_market_share_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND drivetrain = 'Electric vehicle (BEV+PHEV)'
  AND continent IS NOT NULL
GROUP BY continent
ORDER BY total_ev_registrations DESC;


-- ------------------------------------------------------------------------------
-- QUERY 3: HAVING Clause Filtering
-- Business Question: Which countries have achieved a sustained annual EV volume exceeding 100,000 units in 2025?
-- ------------------------------------------------------------------------------
SELECT 
    area AS country,
    year,
    ROUND(SUM(registrations), 0) AS annual_ev_sales,
    ROUND(AVG(share_of_registrations_pct), 2) AS avg_ev_penetration_pct
FROM fact_ev_sales
WHERE is_country = 1
  AND year = 2025
  AND drivetrain = 'Electric vehicle (BEV+PHEV)'
GROUP BY area, year
HAVING SUM(registrations) >= 100000
ORDER BY annual_ev_sales DESC;


-- ------------------------------------------------------------------------------
-- QUERY 4: CASE Expressions & Categorization
-- Business Question: How are vehicle models distributed across driving range performance tiers?
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN range_wltp_km < 300 THEN '1. Urban Commuter (< 300 km)'
        WHEN range_wltp_km BETWEEN 300 AND 499 THEN '2. Standard Range (300 - 499 km)'
        WHEN range_wltp_km BETWEEN 500 AND 649 THEN '3. Long Range (500 - 649 km)'
        WHEN range_wltp_km >= 650 THEN '4. Ultra Long Range (650+ km)'
        ELSE 'Unspecified'
    END AS range_segment,
    COUNT(*) AS model_count,
    ROUND(AVG(battery_capacity_kwh), 1) AS mean_battery_kwh,
    ROUND(AVG(range_wltp_km), 1) AS mean_range_km,
    ROUND(AVG(fast_charge_dc_kw), 1) AS mean_fast_charge_dc_kw
FROM dim_vehicle_specs
WHERE range_wltp_km IS NOT NULL
GROUP BY range_segment
ORDER BY range_segment ASC;


-- ------------------------------------------------------------------------------
-- QUERY 5: NULL Handling with COALESCE and NULLIF
-- Business Question: Safely compute the ratio of oil displaced per EV without division by zero.
-- ------------------------------------------------------------------------------
SELECT 
    area,
    COALESCE(ev_fleet_vehicles, 0) AS fleet_vehicles,
    COALESCE(oil_displaced_kbd_yr, 0) AS oil_displaced_thousand_bbl,
    ROUND(
        COALESCE(oil_displaced_kbd_yr, 0) * 1000.0 / NULLIF(ev_fleet_vehicles, 0),
        2
    ) AS barrels_per_ev_annual
FROM fact_fleet_impact
WHERE is_country = 1
  AND ev_fleet_vehicles > 50000
ORDER BY barrels_per_ev_annual DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- QUERY 6: Common Table Expression (CTE) & Window Functions (RANK, LAG)
-- Business Question: What is the year-over-year annual EV sales growth trajectory for leading nations?
-- ------------------------------------------------------------------------------
WITH annual_country_sales AS (
    SELECT 
        area AS country,
        year,
        SUM(registrations) AS total_sales
    FROM fact_ev_sales
    WHERE is_country = 1
      AND drivetrain = 'Electric vehicle (BEV+PHEV)'
      AND year BETWEEN 2020 AND 2025
    GROUP BY area, year
),
ranked_markets AS (
    SELECT 
        country,
        year,
        total_sales,
        LAG(total_sales, 1) OVER (PARTITION BY country ORDER BY year) AS prev_year_sales,
        RANK() OVER (PARTITION BY year ORDER BY total_sales DESC) AS annual_rank
    FROM annual_country_sales
)
SELECT 
    year,
    annual_rank,
    country,
    ROUND(total_sales, 0) AS sales_units,
    ROUND(prev_year_sales, 0) AS prior_units,
    ROUND(((total_sales - prev_year_sales) * 100.0 / NULLIF(prev_year_sales, 0)), 1) AS yoy_growth_pct
FROM ranked_markets
WHERE annual_rank <= 5
ORDER BY year DESC, annual_rank ASC;


-- ------------------------------------------------------------------------------
-- QUERY 7: Relational Integrity JOIN (Between Sources and Fleet Impact)
-- Demonstrates an inner join respecting grain to attach data provenance.
-- ------------------------------------------------------------------------------
SELECT 
    f.area AS country,
    f.ev_fleet_vehicles,
    f.oil_displaced_kbd_yr,
    s.source_name,
    s.license,
    s.retrieval_date
FROM fact_fleet_impact f
JOIN dataset_sources s ON s.source_key = 'ember_fleet_impact'
WHERE f.is_country = 1
ORDER BY f.ev_fleet_vehicles DESC
LIMIT 5;


-- ------------------------------------------------------------------------------
-- QUERY 8: Vehicle Engineering Efficiency by Manufacturer
-- Business Question: Which brands achieve the highest average driving range per kWh?
-- ------------------------------------------------------------------------------
SELECT 
    brand,
    COUNT(*) AS ev_models_offered,
    ROUND(AVG(battery_capacity_kwh), 1) AS avg_pack_kwh,
    ROUND(AVG(range_wltp_km), 1) AS avg_range_km,
    ROUND(AVG(efficiency_km_per_kwh), 2) AS avg_km_per_kwh
FROM dim_vehicle_specs
WHERE battery_capacity_kwh > 0
  AND range_wltp_km > 0
GROUP BY brand
HAVING COUNT(*) >= 3
ORDER BY avg_km_per_kwh DESC
LIMIT 10;
