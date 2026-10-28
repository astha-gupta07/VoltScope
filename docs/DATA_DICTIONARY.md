# VoltScope Data Dictionary & Schema Reference

This document provides granular technical definitions, data types, measurement units, provenance sources, and null handling policies for all relational tables in `database/voltscope.db` and exported Tableau extracts in `data/exports/tableau/`.

---

## 1. Table: `fact_ev_sales`

- **Purpose**: Tracks monthly new passenger car registrations, year-over-year percentage growth, and market penetration shares across countries and drivetrains.
- **Grain**: One row per geographical Area (`area`), Month (`date`), and Drivetrain (`drivetrain`).
- **Primary / Natural Key**: `(area, date, drivetrain)`
- **Source**: Ember Monthly EV Sales Data (`monthly_ev_sales.csv`), CC BY 4.0.

| Field Name | SQLite Data Type | Measurement Unit | Nullable | Description & Domain Values |
| :--- | :--- | :--- | :--- | :--- |
| `sale_id` | `INTEGER PRIMARY KEY` | Dimensionless | No | Auto-incrementing surrogate primary key. |
| `area` | `TEXT` | Name | No | Sovereign country name or supranational region (e.g., 'Germany', 'United States', 'World', 'European Union'). |
| `iso_3_code` | `TEXT` | ISO 3166-1 alpha-3 | Yes | Standard 3-letter country code (e.g., 'DEU', 'USA', 'CHN'). Null for multi-nation regional aggregates. |
| `area_type` | `TEXT` | Category | No | Geographical level: `'Country or economy'` or `'Region'`. |
| `is_country` | `BOOLEAN` | Boolean Flag | No | `1` (TRUE) for sovereign nations; `0` (FALSE) for regional totals. Used to prevent double-counting. |
| `date` | `TEXT` | ISO-8601 Date | No | First calendar day of reporting month (`YYYY-MM-01`). Spans `2005-01-01` to `2026-09-01`. |
| `year` | `INTEGER` | Calendar Year | No | Extracted integer year (`2005` to `2026`). |
| `month` | `INTEGER` | Calendar Month | No | Extracted month of year (`1` to `12`). |
| `data_frequency` | `TEXT` | Frequency | No | Ingestion cadence; defaults to `'Monthly'`. |
| `drivetrain` | `TEXT` | Powertrain Category | No | Categorical powertrain type: `'Battery electric'`, `'Plug-in hybrid'`, `'Hybrid'`, `'Petrol'`, `'Diesel'`, `'Ethanol/petrol blend'`, `'Combustion (unspecified)'`, `'Other'`, `'Electric vehicle (BEV+PHEV)'`, `'All drivetrains'`. |
| `is_aggregate_drivetrain` | `BOOLEAN` | Boolean Flag | No | `1` (TRUE) for summary aggregates (`'Electric vehicle (BEV+PHEV)'` & `'All drivetrains'`); `0` (FALSE) for granular drivetrains. |
| `registrations` | `REAL` | Number of Vehicles | Yes | Quantity of newly registered passenger vehicles in the month. Missing if publisher does not report that specific powertrain. |
| `registrations_yoy_change`| `REAL` | Number of Vehicles | Yes | Change in registrations relative to the same calendar month of the preceding year. |
| `registrations_yoy_change_pct` | `REAL` | Percentage (`%`) | Yes | Year-over-year percentage growth in registrations. Blank for baseline months. |
| `share_of_registrations_pct` | `REAL` | Percentage (`%`) | Yes | Share of total passenger car registrations represented by this drivetrain in that month (relative to `'All drivetrains'`). |
| `ytd_registrations` | `REAL` | Number of Vehicles | Yes | Cumulative year-to-date registrations, resetting each January 1st. |
| `ytd_share_pct` | `REAL` | Percentage (`%`) | Yes | Year-to-date market share percentage. |
| `rolling_12m_registrations` | `REAL` | Number of Vehicles | Yes | Cumulative registrations over the preceding 12 calendar months (removes seasonal seasonality). |
| `rolling_12m_share_pct` | `REAL` | Percentage (`%`) | Yes | 12-month rolling market share percentage. |
| `continent` | `TEXT` | Continent Name | Yes | Geographic continent (`'Europe'`, `'Asia'`, `'Americas'`, `'Oceania'`, `'Africa'`). |
| `ember_region` | `TEXT` | Region Name | Yes | Ember analytical reporting region. |
| `is_eu_member` | `BOOLEAN` | Boolean Flag | No | Member of the European Union (`1` / `0`). |
| `is_oecd_member` | `BOOLEAN` | Boolean Flag | No | Member of the OECD (`1` / `0`). |
| `is_g20_member` | `BOOLEAN` | Boolean Flag | No | Member of the G20 (`1` / `0`). |
| `is_g7_member` | `BOOLEAN` | Boolean Flag | No | Member of the G7 (`1` / `0`). |
| `is_asean_member` | `BOOLEAN` | Boolean Flag | No | Member of ASEAN (`1` / `0`). |

---

## 2. Table: `fact_fleet_impact`

- **Purpose**: Quantifies cumulative national EV fleet sizes, power grid demand, and petroleum displacement metrics.
- **Grain**: One row per geographical Area (`area`) reflecting the latest available reporting date.
- **Primary / Natural Key**: `area`
- **Source**: Ember EV Fleet & Oil Displacement Impact Data (`monthly_ev_fleet_impact.csv`), CC BY 4.0.

| Field Name | SQLite Data Type | Measurement Unit | Nullable | Description & Domain Values |
| :--- | :--- | :--- | :--- | :--- |
| `impact_id` | `INTEGER PRIMARY KEY` | Dimensionless | No | Auto-incrementing surrogate primary key. |
| `area` | `TEXT UNIQUE` | Name | No | Country or regional aggregate name. |
| `iso_3_code` | `TEXT` | ISO 3166-1 alpha-3 | Yes | 3-letter country code. |
| `area_type` | `TEXT` | Category | No | `'Country or economy'` or `'Region'`. |
| `is_country` | `BOOLEAN` | Boolean Flag | No | `1` for sovereign countries; `0` for supranational totals. |
| `latest_available_date` | `TEXT` | ISO-8601 Date | No | Date of the latest data point incorporated into the cumulative fleet model. |
| `ev_fleet_vehicles` | `REAL` | Number of Vehicles | No | Estimated operational fleet of pure electric and plug-in hybrid cars. |
| `electricity_demand_gwh_yr`| `REAL` | Gigawatt-hours / yr | Yes | Estimated annual electrical power required to charge the national EV fleet. |
| `oil_displaced_kbd_yr` | `REAL` | Thousand Barrels / yr | Yes | Barrels of crude oil equivalent displaced annually by replacing internal combustion vehicles. |
| `oil_displaced_usd_million_yr`| `REAL` | USD Million ($M) | Yes | Economic value of oil displaced based on 6-month average Brent crude price. |
| `brent_price_usd` | `REAL` | USD per Barrel ($/bbl)| Yes | 6-month benchmark crude oil price utilized in the economic displacement model. |

---

## 3. Table: `dim_vehicle_specs`

- **Purpose**: Dimension catalog of electrified passenger vehicle technical specifications.
- **Grain**: One row per unique vehicle model generation (`model_id`).
- **Primary / Natural Key**: `model_id`
- **Source**: autoseeker.eu Open Car Specifications (`models.csv`), CC BY 4.0.

| Field Name | SQLite Data Type | Measurement Unit | Nullable | Description & Domain Values |
| :--- | :--- | :--- | :--- | :--- |
| `model_id` | `TEXT PRIMARY KEY` | Slug String | No | URL-safe unique model slug (e.g., `'tesla-model-y-2024'`, `'hyundai-ioniq-5-2024'`). |
| `brand` | `TEXT` | Brand Name | No | Automotive manufacturer / brand name (e.g., `'Tesla'`, `'BMW'`, `'Volkswagen'`). |
| `model_name` | `TEXT` | Model Name | No | Commercial vehicle model designation (e.g., `'Model Y'`, `'ID.4'`, `'Ioniq 5'`). |
| `generation` | `TEXT` | Generation | Yes | Vehicle generation and facelift phase identifier. |
| `body_category` | `TEXT` | Category | No | Standardized English body style: `'SUV / Crossover'`, `'Sedan'`, `'Hatchback'`, `'Station Wagon'`, `'Coupe'`, `'Convertible'`, `'MPV / Minivan'`, `'Other'`. |
| `raw_body_style` | `TEXT` | Raw Dutch String | Yes | Original raw body classification from source file. |
| `fuel_type` | `TEXT` | Fuel String | No | Raw powertrain fuel string (e.g., `'ev'`, `'ev\|hybride'`, `'phev'`). |
| `drivetrain_class` | `TEXT` | Classification | No | Clean classification: `'Pure BEV'` or `'Plug-in Hybrid / Multi-fuel'`. |
| `release_year` | `INTEGER` | Calendar Year | Yes | Year of initial production or model year introduction. |
| `power_hp` | `REAL` | Horsepower (hp) | Yes | Total system output in metric horsepower. |
| `battery_capacity_kwh` | `REAL` | Kilowatt-hours (kWh) | Yes | Usable battery pack energy capacity. |
| `range_wltp_km` | `REAL` | Kilometres (km) | Yes | Certified driving range under the Worldwide Harmonised Light Vehicles Test Procedure (WLTP). |
| `efficiency_km_per_kwh`| `REAL` | Kilometres per kWh | Yes | Calculated engineering efficiency: `range_wltp_km / battery_capacity_kwh`. |
| `consumption_kwh_100km` | `REAL` | kWh per 100 km | Yes | Energy consumption rating per 100 km driven. |
| `fast_charge_dc_kw` | `REAL` | Kilowatts (kW) | Yes | Maximum supported DC fast-charging power. |
| `has_fast_charging` | `BOOLEAN` | Boolean Flag | No | `1` (TRUE) if model supports DC fast charging (`fast_charge_dc_kw > 0`); `0` otherwise. |
| `towing_capacity_kg` | `REAL` | Kilograms (kg) | Yes | Maximum braked towing weight capacity. |
| `cargo_volume_liters` | `REAL` | Liters (L) | Yes | Boot / luggage capacity with seats up. |
| `seats` | `INTEGER` | Seating Capacity | Yes | Number of passenger seating positions. |
| `doors` | `INTEGER` | Door Count | Yes | Number of vehicle doors. |

---

## 4. Table: `dataset_sources`

- **Purpose**: Stores provenance metadata, licensing terms, and retrieval dates for all ingested sources.
- **Grain**: One row per registered data source key.
- **Primary Key**: `source_key`

| Field Name | SQLite Data Type | Description |
| :--- | :--- | :--- |
| `source_key` | `TEXT PRIMARY KEY` | Unique programmatic identifier (`'ember_monthly_sales'`, `'ember_fleet_impact'`, `'autoseeker_models'`). |
| `source_name` | `TEXT` | Formal dataset title. |
| `publisher` | `TEXT` | Publishing organization or individual think tank. |
| `source_url` | `TEXT` | Public downloadable URL. |
| `license` | `TEXT` | Intellectual property and data reuse license (`'Creative Commons Attribution 4.0 International (CC BY 4.0)'`). |
| `retrieval_date` | `TEXT` | Date of retrieval / ingestion into VoltScope (`YYYY-MM-DD`). |
| `record_count` | `INTEGER` | Number of validated rows ingested into the database. |
| `description` | `TEXT` | Detailed scope summary. |
