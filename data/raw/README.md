# VoltScope Raw Datasets & Data Provenance

This directory stores raw, unmodified data files collected for the VoltScope project.
All datasets are governed by public, open-access licenses and must never be altered in place.

## Data Source Catalog

### 1. Ember Monthly EV Sales Data
- **Publisher**: Ember (Registered energy think tank, UK/Global)
- **Direct Download URL**: `https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/transport/outputs/monthly_ev_sales.csv`
- **Web Portal**: `https://ember-energy.org/data/monthly-ev-sales-data/`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Time Coverage**: January 2005 – September 2026 (Monthly frequency)
- **Geographical Coverage**: 56 sovereign nations, European Union (EU-27), and World total
- **Local Filename**: `data/raw/monthly_ev_sales.csv`
- **Primary Metrics**:
  - `Registrations`: New passenger car registrations in month
  - `Share of registrations (%)`: EV share relative to all drivetrains
  - `YoY change (%)`: Year-over-year percentage growth
  - `Drivetrain`: Battery electric (BEV), Plug-in hybrid (PHEV), Hybrid (HEV), Petrol, Diesel, Ethanol/petrol, Combustion (unspecified)
  - `Is aggregate drivetrain`: Boolean flag distinguishing aggregates from granular drivetrains

### 2. Ember EV Fleet & Oil Displacement Impact Data
- **Publisher**: Ember
- **Direct Download URL**: `https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/transport/outputs/monthly_ev_fleet_impact.csv`
- **Web Portal**: `https://ember-energy.org/data/monthly-ev-sales-data/`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Time Coverage**: Latest available cumulative snapshot per country (through Q3 2026)
- **Local Filename**: `data/raw/monthly_ev_fleet_impact.csv`
- **Primary Metrics**:
  - `EV fleet (vehicles)`: Estimated active cumulative electric fleet
  - `EV fleet electricity demand (GWh per year)`: Annual electricity consumed
  - `Oil displaced (thousand barrels of oil equivalent per year)`: Direct petroleum displacement
  - `Value of oil displaced (USD million per year)`: Monetary economic saving based on 6-month Brent crude average

### 3. autoseeker Open Car Specifications
- **Publisher**: autoseeker.eu (Dennis de Kruijf)
- **Direct Download URL**: `https://autoseeker.eu/data/models.csv`
- **Web Portal**: `https://autoseeker.eu/en/data/`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Time Coverage**: Current production & historical modern EV models (build years 2012–2026)
- **Local Filename**: `data/raw/autoseeker_models.csv`
- **Scope**: Filtered strictly to electrified vehicle models (`ev`, `phev`)
- **Primary Metrics**:
  - `merk`: Brand / Manufacturer
  - `model`: Commercial model name
  - `carrosserie`: Body style (SUV, Sedan, Hatchback, etc.)
  - `batterij_kwh`: Usable battery capacity (kWh)
  - `wltp_range_km`: WLTP certified driving range (km)
  - `laadvermogen_dc_kw`: Peak DC fast-charging capacity (kW)
  - `verbruik_wltp_kwh_100km`: Certified energy consumption (kWh/100km)
  - `vermogen_pk`: System power output in horsepower (hp)

---

## Ingestion & Manual Fallback Instructions

To download all raw datasets automatically:
```powershell
python scripts/download_data.py
```

If an active internet connection is unavailable or the URLs are blocked by network policies:
1. Open your web browser and navigate to the URLs listed above.
2. Download the three CSV files.
3. Save them into `data/raw/` with the exact names:
   - `monthly_ev_sales.csv`
   - `monthly_ev_fleet_impact.csv`
   - `autoseeker_models.csv`
4. Run `python scripts/validate_data.py` to verify schema and checksums.
