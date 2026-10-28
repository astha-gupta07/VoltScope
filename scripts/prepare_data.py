"""
VoltScope - Data Preparation & Cleaning Module
Transforms raw datasets into typed, normalized, and analysis-ready structures.
Calculates derived features, cleans text and categories, and produces audit logs.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATASET_SOURCES, PROCESSED_DATA_DIR


def clean_body_category(val: str) -> str:
    """Normalize body style names to standard English vehicle categories."""
    if not isinstance(val, str) or not val.strip():
        return "Unknown"
    v = val.strip().lower()
    if any(k in v for k in ["suv", "crossover"]):
        return "SUV / Crossover"
    elif any(k in v for k in ["hatchback", "liftback", "fastback"]):
        return "Hatchback"
    elif "sedan" in v:
        return "Sedan"
    elif any(k in v for k in ["stationwagen", "stationwagon", "shooting brake"]):
        return "Station Wagon"
    elif "coupe" in v or "coup" in v:
        return "Coupe"
    elif "cabrio" in v or "convertible" in v:
        return "Convertible"
    elif "mpv" in v or "minivan" in v or "van" in v:
        return "MPV / Minivan"
    return "Other"


def clean_ev_sales(raw_path: Path) -> tuple[pd.DataFrame, dict]:
    """Clean and normalize Ember monthly EV sales data."""
    df = pd.read_csv(raw_path, low_memory=False)
    initial_rows = len(df)
    
    # Rename columns to standardized snake_case
    col_map = {
        "Area": "area",
        "ISO 3 code": "iso_3_code",
        "Area type": "area_type",
        "Date": "date",
        "Data frequency": "data_frequency",
        "Drivetrain": "drivetrain",
        "Is aggregate drivetrain": "is_aggregate_drivetrain",
        "Registrations": "registrations",
        "Registrations YoY change": "registrations_yoy_change",
        "Registrations YoY change (%)": "registrations_yoy_change_pct",
        "Share of registrations (%)": "share_of_registrations_pct",
        "Year-to-date registrations": "ytd_registrations",
        "Year-to-date share of registrations (%)": "ytd_share_pct",
        "Rolling 12-month registrations": "rolling_12m_registrations",
        "Rolling 12-month share of registrations (%)": "rolling_12m_share_pct",
        "Continent": "continent",
        "Ember region": "ember_region",
        "EU member": "is_eu_member",
        "OECD member": "is_oecd_member",
        "G20 member": "is_g20_member",
        "G7 member": "is_g7_member",
        "ASEAN member": "is_asean_member"
    }
    
    # Select available columns
    available_map = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=available_map)[list(available_map.values())]
    
    # Parse dates and extract components
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "area", "drivetrain"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # Boolean conversions
    for b_col in ["is_aggregate_drivetrain", "is_eu_member", "is_oecd_member", "is_g20_member", "is_g7_member", "is_asean_member"]:
        if b_col in df.columns:
            df[b_col] = df[b_col].fillna(False).astype(bool)
            
    # Numeric conversions
    numeric_cols = [
        "registrations", "registrations_yoy_change", "registrations_yoy_change_pct",
        "share_of_registrations_pct", "ytd_registrations", "ytd_share_pct",
        "rolling_12m_registrations", "rolling_12m_share_pct"
    ]
    for n_col in numeric_cols:
        if n_col in df.columns:
            df[n_col] = pd.to_numeric(df[n_col], errors="coerce")
            
    # Add helper flag: is sovereign country vs multi-national region
    df["is_country"] = df["area_type"].astype(str).str.strip().eq("Country or economy")
    
    # Deduplicate by primary key (area, date, drivetrain)
    dups_removed = df.duplicated(subset=["area", "date", "drivetrain"]).sum()
    df = df.drop_duplicates(subset=["area", "date", "drivetrain"])
    
    final_rows = len(df)
    
    quality_summary = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "duplicates_removed": int(dups_removed),
        "excluded_invalid_dates": int(initial_rows - final_rows - dups_removed),
        "areas_count": int(df["area"].nunique()),
        "countries_count": int(df[df["is_country"]]["area"].nunique()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "null_counts": {c: int(df[c].isna().sum()) for c in df.columns}
    }
    
    return df, quality_summary


def clean_fleet_impact(raw_path: Path) -> tuple[pd.DataFrame, dict]:
    """Clean and normalize Ember EV Fleet & Oil Displacement Impact data."""
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    col_map = {
        "Area": "area",
        "ISO 3 code": "iso_3_code",
        "Area type": "area_type",
        "Latest available date": "latest_available_date",
        "EV fleet (vehicles)": "ev_fleet_vehicles",
        "EV fleet electricity demand (GWh per year)": "electricity_demand_gwh_yr",
        "Oil displaced (thousand barrels of oil equivalent per year)": "oil_displaced_kbd_yr",
        "Value of oil displaced (USD million per year)": "oil_displaced_usd_million_yr",
        "Brent price 6-month average (USD/bbl)": "brent_price_usd"
    }
    
    available_map = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=available_map)[list(available_map.values())]
    
    df["latest_available_date"] = pd.to_datetime(df["latest_available_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    numeric_cols = [
        "ev_fleet_vehicles", "electricity_demand_gwh_yr",
        "oil_displaced_kbd_yr", "oil_displaced_usd_million_yr", "brent_price_usd"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            
    df["is_country"] = df["area_type"].astype(str).str.strip().eq("Country or economy")
    df = df.drop_duplicates(subset=["area"])
    final_rows = len(df)
    
    quality_summary = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "countries_covered": int(df[df["is_country"]]["area"].nunique()),
        "global_fleet_vehicles_reported": float(df[df["area"] == "World"]["ev_fleet_vehicles"].sum()),
        "null_counts": {c: int(df[c].isna().sum()) for c in df.columns}
    }
    
    return df, quality_summary


def clean_vehicle_specs(raw_path: Path) -> tuple[pd.DataFrame, dict]:
    """Filter and clean autoseeker specifications for EV/PHEV models."""
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # Filter strictly to models featuring electric powertrain
    is_ev = df["fuels"].fillna("").apply(
        lambda f: any(x in str(f).lower().split("|") for x in ["ev", "phev"])
    )
    df = df[is_ev].copy()
    ev_filtered_rows = len(df)
    
    # Map and rename
    col_map = {
        "slug": "model_id",
        "merk": "brand",
        "model": "model_name",
        "generatie": "generation",
        "carrosserie": "raw_body_style",
        "fuels": "fuel_type",
        "bouwjaarVan": "release_year",
        "vermogen_pk": "power_hp",
        "wltp_range_km": "range_wltp_km",
        "batterij_kwh": "battery_capacity_kwh",
        "laadvermogen_dc_kw": "fast_charge_dc_kw",
        "verbruik_wltp_kwh_100km": "consumption_kwh_100km",
        "trekgewicht_geremd_kg": "towing_capacity_kg",
        "kofferbak_liter": "cargo_volume_liters",
        "zitplaatsen": "seats",
        "deuren": "doors"
    }
    available_map = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=available_map)[list(available_map.values())]
    
    # Clean text columns
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model_name"] = df["model_name"].astype(str).str.strip()
    df["generation"] = df["generation"].fillna("Standard").astype(str).str.strip()
    
    # Standardize body category
    df["body_category"] = df["raw_body_style"].apply(clean_body_category)
    
    # Numeric conversions
    numeric_cols = [
        "release_year", "power_hp", "range_wltp_km", "battery_capacity_kwh",
        "fast_charge_dc_kw", "consumption_kwh_100km", "towing_capacity_kg",
        "cargo_volume_liters", "seats", "doors"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            
    # Calculate derived engineering metrics:
    # 1. Driving efficiency (km per kWh)
    df["efficiency_km_per_kwh"] = np.where(
        (df["battery_capacity_kwh"] > 0) & (df["range_wltp_km"] > 0),
        (df["range_wltp_km"] / df["battery_capacity_kwh"]).round(2),
        np.nan
    )
    
    # 2. Fast charging flag
    df["has_fast_charging"] = df["fast_charge_dc_kw"].fillna(0) > 0
    
    # 3. Drivetrain category flag
    df["drivetrain_class"] = np.where(
        df["fuel_type"].str.contains("ev", case=False, na=False) & ~df["fuel_type"].str.contains("benzine|diesel|hybride", case=False, na=False),
        "Pure BEV",
        "Plug-in Hybrid / Multi-fuel"
    )
    
    # Deduplicate on model_id
    dups_removed = df.duplicated(subset=["model_id"]).sum()
    df = df.drop_duplicates(subset=["model_id"])
    final_rows = len(df)
    
    # Identify high-performance outliers (documented, not deleted!)
    high_range_models = df[df["range_wltp_km"] >= 700][["brand", "model_name", "range_wltp_km", "battery_capacity_kwh"]].to_dict(orient="records")
    
    quality_summary = {
        "raw_total_models": initial_rows,
        "ev_phev_models_retained": final_rows,
        "duplicates_removed": int(dups_removed),
        "distinct_brands": int(df["brand"].nunique()),
        "body_categories_distribution": df["body_category"].value_counts().to_dict(),
        "drivetrain_class_distribution": df["drivetrain_class"].value_counts().to_dict(),
        "avg_battery_capacity_kwh": round(float(df["battery_capacity_kwh"].mean()), 2) if not df["battery_capacity_kwh"].isna().all() else 0,
        "avg_range_wltp_km": round(float(df["range_wltp_km"].mean()), 2) if not df["range_wltp_km"].isna().all() else 0,
        "documented_high_performance_outliers": high_range_models,
        "null_counts": {c: int(df[c].isna().sum()) for c in df.columns}
    }
    
    return df, quality_summary


def run_preparation() -> dict:
    """Execute full data preparation pipeline and write outputs to data/processed/."""
    print("=" * 70)
    print(" VoltScope Data Preparation & Transformation Pipeline")
    print("=" * 70)
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    full_report = {
        "preparation_timestamp": pd.Timestamp.now().isoformat(),
        "datasets": {}
    }
    
    # 1. EV Sales
    print("[*] Processing Ember Monthly EV Sales...")
    df_sales, summary_sales = clean_ev_sales(DATASET_SOURCES["ember_monthly_sales"]["local_file"])
    sales_out = PROCESSED_DATA_DIR / "cleaned_ev_sales.csv"
    df_sales.to_csv(sales_out, index=False)
    print(f"    [+] Saved {len(df_sales):,} clean rows to {sales_out.name}")
    full_report["datasets"]["cleaned_ev_sales"] = summary_sales
    
    # 2. Fleet Impact
    print("[*] Processing Ember Fleet & Oil Displacement Impact...")
    df_fleet, summary_fleet = clean_fleet_impact(DATASET_SOURCES["ember_fleet_impact"]["local_file"])
    fleet_out = PROCESSED_DATA_DIR / "cleaned_fleet_impact.csv"
    df_fleet.to_csv(fleet_out, index=False)
    print(f"    [+] Saved {len(df_fleet):,} clean rows to {fleet_out.name}")
    full_report["datasets"]["cleaned_fleet_impact"] = summary_fleet
    
    # 3. Vehicle Specifications
    print("[*] Processing autoseeker EV Specifications...")
    df_specs, summary_specs = clean_vehicle_specs(DATASET_SOURCES["autoseeker_models"]["local_file"])
    specs_out = PROCESSED_DATA_DIR / "cleaned_vehicle_specs.csv"
    df_specs.to_csv(specs_out, index=False)
    print(f"    [+] Saved {len(df_specs):,} clean EV models to {specs_out.name}")
    full_report["datasets"]["cleaned_vehicle_specs"] = summary_specs
    
    # Write complete data quality and audit report
    report_out = PROCESSED_DATA_DIR / "data_quality_report.json"
    with open(report_out, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
        
    print(f"\n[+] Full Data Quality Audit Report generated at {report_out.name}")
    return full_report


if __name__ == "__main__":
    run_preparation()
