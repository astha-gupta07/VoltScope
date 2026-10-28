"""
VoltScope - Data Validation Module
Performs schema, type, range, uniqueness, and completeness checks across raw datasets.
Generates structured audit logs and quality metrics before any cleaning or loading.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATASET_SOURCES, PROCESSED_DATA_DIR


def validate_ev_sales(df: pd.DataFrame) -> dict:
    """Validate Ember monthly EV sales dataset."""
    expected_cols = [
        "Area", "ISO 3 code", "Area type", "Date", "Drivetrain",
        "Is aggregate drivetrain", "Registrations"
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    
    # Check date format
    date_series = pd.to_datetime(df["Date"], errors="coerce")
    invalid_dates = df[date_series.isna()]["Date"].dropna().count()
    
    # Check numeric ranges
    neg_registrations = (df["Registrations"].dropna() < 0).sum()
    
    # Duplicate check on natural key: (Area, Date, Drivetrain)
    dup_keys = df.duplicated(subset=["Area", "Date", "Drivetrain"]).sum()
    
    # Missing values
    null_counts = {col: int(df[col].isna().sum()) for col in expected_cols}
    
    # Granular summary
    areas = df["Area"].nunique()
    drivetrains = df["Drivetrain"].dropna().unique().tolist()
    min_date = str(df["Date"].min())
    max_date = str(df["Date"].max())
    
    passed = (len(missing_cols) == 0) and (invalid_dates == 0) and (neg_registrations == 0)
    
    return {
        "dataset": "Ember Monthly EV Sales",
        "passed": bool(passed),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_expected_columns": missing_cols,
        "invalid_dates": int(invalid_dates),
        "negative_registrations": int(neg_registrations),
        "duplicate_natural_keys": int(dup_keys),
        "null_counts": null_counts,
        "distinct_areas": int(areas),
        "date_range": [min_date, max_date],
        "drivetrains": drivetrains
    }


def validate_fleet_impact(df: pd.DataFrame) -> dict:
    """Validate Ember fleet and oil displacement impact dataset."""
    expected_cols = [
        "Area", "ISO 3 code", "Area type", "Latest available date",
        "EV fleet (vehicles)", "EV fleet electricity demand (GWh per year)",
        "Oil displaced (thousand barrels of oil equivalent per year)"
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    
    # Check uniqueness of Area
    dup_areas = df.duplicated(subset=["Area"]).sum()
    
    # Check non-negative metrics
    fleet = pd.to_numeric(df.get("EV fleet (vehicles)"), errors="coerce")
    neg_fleet = (fleet < 0).sum()
    
    passed = (len(missing_cols) == 0) and (dup_areas == 0) and (neg_fleet == 0)
    
    return {
        "dataset": "Ember EV Fleet & Oil Displacement Impact",
        "passed": bool(passed),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_expected_columns": missing_cols,
        "duplicate_areas": int(dup_areas),
        "negative_fleet_values": int(neg_fleet),
        "areas_covered": int(df["Area"].nunique())
    }


def validate_vehicle_specs(df: pd.DataFrame) -> dict:
    """Validate autoseeker EV model specifications."""
    expected_cols = [
        "slug", "merk", "model", "carrosserie", "fuels",
        "vermogen_pk", "wltp_range_km", "batterij_kwh"
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    
    # Duplicate slugs
    dup_slugs = df.duplicated(subset=["slug"]).sum()
    
    # Identify EV/PHEV models
    is_ev = df["fuels"].fillna("").apply(
        lambda f: any(x in str(f).lower().split("|") for x in ["ev", "phev"])
    )
    ev_count = int(is_ev.sum())
    
    # For EV rows, validate range and battery
    ev_df = df[is_ev].copy()
    ranges = pd.to_numeric(ev_df["wltp_range_km"], errors="coerce")
    batteries = pd.to_numeric(ev_df["batterij_kwh"], errors="coerce")
    
    invalid_ranges = ((ranges <= 0) | (ranges > 1500)).sum()
    invalid_batteries = ((batteries <= 0) | (batteries > 300)).sum()
    
    passed = (len(missing_cols) == 0) and (dup_slugs == 0) and (ev_count > 0)
    
    return {
        "dataset": "autoseeker Open Car Specifications",
        "passed": bool(passed),
        "total_rows": len(df),
        "ev_phev_models_found": ev_count,
        "missing_expected_columns": missing_cols,
        "duplicate_slugs": int(dup_slugs),
        "invalid_wltp_range_count": int(invalid_ranges),
        "invalid_battery_kwh_count": int(invalid_batteries),
        "distinct_brands": int(ev_df["merk"].nunique()) if ev_count > 0 else 0
    }


def run_validation() -> dict:
    """Run full validation suite on raw data files."""
    print("=" * 70)
    print(" VoltScope Data Integrity & Schema Validation")
    print("=" * 70)
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    report = {"validation_timestamp": pd.Timestamp.now().isoformat(), "results": {}}
    all_passed = True
    
    for key, info in DATASET_SOURCES.items():
        file_path = info["local_file"]
        if not file_path.exists():
            print(f"[!] File not found: {file_path}")
            report["results"][key] = {"error": f"File not found: {file_path}"}
            all_passed = False
            continue
            
        print(f"[*] Validating {info['name']} ({file_path.name})...")
        try:
            df = pd.read_csv(file_path, low_memory=False)
            if key == "ember_monthly_sales":
                res = validate_ev_sales(df)
            elif key == "ember_fleet_impact":
                res = validate_fleet_impact(df)
            elif key == "autoseeker_models":
                res = validate_vehicle_specs(df)
            else:
                res = {"status": "unrecognized_dataset"}
                
            report["results"][key] = res
            status_symbol = "[+]" if res.get("passed", False) else "[!]"
            print(f"    {status_symbol} Passed: {res.get('passed', False)} | Rows: {res.get('total_rows'):,}")
            if not res.get("passed", False):
                all_passed = False
        except Exception as e:
            print(f"    [!] Error validating {file_path.name}: {e}")
            report["results"][key] = {"error": str(e), "passed": False}
            all_passed = False
            
    report["overall_passed"] = all_passed
    report_file = PROCESSED_DATA_DIR / "validation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n[+] Validation report written to {report_file.name}")
    print(f"[*] Overall Validation Passed: {all_passed}")
    return report


if __name__ == "__main__":
    rep = run_validation()
    if not rep.get("overall_passed", False):
        sys.exit(1)
    sys.exit(0)
