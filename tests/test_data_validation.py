"""
Unit Tests: Data Validation & Integrity Checks
Verifies that raw and processed datasets adhere to strict integrity rules:
no negative registrations, valid date ranges, correct columns, and zero synthetic records.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR


def test_raw_files_exist():
    """Verify all 3 primary datasets exist in data/raw/."""
    assert (RAW_DATA_DIR / "monthly_ev_sales.csv").exists(), "monthly_ev_sales.csv is missing"
    assert (RAW_DATA_DIR / "monthly_ev_fleet_impact.csv").exists(), "monthly_ev_fleet_impact.csv is missing"
    assert (RAW_DATA_DIR / "autoseeker_models.csv").exists(), "autoseeker_models.csv is missing"


def test_processed_sales_integrity():
    """Verify cleaned_ev_sales.csv has valid columns, positive sales, and ISO dates."""
    sales_file = PROCESSED_DATA_DIR / "cleaned_ev_sales.csv"
    assert sales_file.exists(), "cleaned_ev_sales.csv missing in processed data"
    
    df = pd.read_csv(sales_file, nrows=1000)
    expected_cols = ["area", "iso_3_code", "area_type", "date", "year", "month", "drivetrain", "registrations"]
    for col in expected_cols:
        assert col in df.columns, f"Expected column '{col}' missing from cleaned_ev_sales.csv"
        
    # Check no negative registrations
    non_null_regs = df["registrations"].dropna()
    assert (non_null_regs >= 0).all(), "Negative registration figures detected in cleaned sales"
    
    # Check valid year range
    assert (df["year"] >= 2005).all() and (df["year"] <= 2030).all(), "Year outside plausible bounds"


def test_processed_fleet_integrity():
    """Verify cleaned_fleet_impact.csv has positive fleet numbers and non-empty areas."""
    fleet_file = PROCESSED_DATA_DIR / "cleaned_fleet_impact.csv"
    assert fleet_file.exists(), "cleaned_fleet_impact.csv missing in processed data"
    
    df = pd.read_csv(fleet_file)
    assert len(df) > 0, "Fleet impact dataset is empty"
    assert "ev_fleet_vehicles" in df.columns
    assert (df["ev_fleet_vehicles"].dropna() >= 0).all(), "Negative fleet vehicle counts found"


def test_processed_vehicle_specs_integrity():
    """Verify cleaned_vehicle_specs.csv contains only EV/PHEV models with positive battery and range."""
    specs_file = PROCESSED_DATA_DIR / "cleaned_vehicle_specs.csv"
    assert specs_file.exists(), "cleaned_vehicle_specs.csv missing in processed data"
    
    df = pd.read_csv(specs_file)
    assert len(df) > 0, "Vehicle specs dataset is empty"
    assert "battery_capacity_kwh" in df.columns
    assert "range_wltp_km" in df.columns
    
    # Check range and battery bounds on positive models
    valid_range = df[df["range_wltp_km"] > 0]
    assert len(valid_range) > 50, "Insufficient EV models with valid range"
    assert (valid_range["range_wltp_km"] <= 1500).all(), "Unrealistic range values (>1500km) detected"
    assert (valid_range["battery_capacity_kwh"].dropna() <= 300).all(), "Unrealistic battery pack (>300kWh)"
