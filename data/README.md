# VoltScope Data Directory Structure

This directory manages the lifecycle of data within VoltScope across three distinct tiers:

```
data/
├── raw/               # Immutable original files retrieved from Ember & autoseeker
├── processed/         # Cleaned, typed, normalized CSV & summary metadata
└── exports/
    └── tableau/       # Formatted, Tableau-ready CSV exports for extract connections
```

## Directory Responsibilities

1. **`data/raw/`**:
   - Contains original source files: `monthly_ev_sales.csv`, `monthly_ev_fleet_impact.csv`, `autoseeker_models.csv`.
   - Populated by `scripts/download_data.py`.
   - Never edit files here manually.

2. **`data/processed/`**:
   - Cleaned, validated, and normalized data produced by `scripts/prepare_data.py`.
   - Contains `cleaned_ev_sales.csv`, `cleaned_fleet_impact.csv`, `cleaned_vehicle_specs.csv`, and `data_quality_report.json`.
   - English vehicle body categories, standard ISO-8601 dates, typed numerics.

3. **`data/exports/tableau/`**:
   - Denormalized, analysis-ready CSV extracts created by `scripts/export_tableau_data.py`.
   - Specifically structured for easy drag-and-drop ingestion into Tableau Desktop and Tableau Public.
   - Includes:
     - `tableau_ev_market_sales.csv`
     - `tableau_ev_fleet_sustainability.csv`
     - `tableau_vehicle_specifications.csv`
     - `tableau_drivetrain_mix_annual.csv`
     - `tableau_top_markets_summary.csv`
