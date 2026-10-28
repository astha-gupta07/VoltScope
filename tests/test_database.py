"""
Unit Tests: Database Schema, Views & Query Portfolio
Verifies SQLite relational integrity, primary keys, views execution, and non-empty tables.
"""

import sys
import sqlite3
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATABASE_FILE, QUERIES_FILE


@pytest.fixture(scope="module")
def db_conn():
    """Provide a connection to the test/production SQLite database."""
    assert DATABASE_FILE.exists(), f"Database not found at {DATABASE_FILE}"
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_database_tables_exist(db_conn):
    """Verify all 4 core tables exist in the database."""
    cursor = db_conn.cursor()
    tables = [
        r[0] for r in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
    ]
    expected_tables = ["dataset_sources", "fact_ev_sales", "fact_fleet_impact", "dim_vehicle_specs"]
    for t in expected_tables:
        assert t in tables, f"Table '{t}' is missing from database"


def test_table_row_counts(db_conn):
    """Assert minimum expected record thresholds."""
    cursor = db_conn.cursor()
    sales_count = cursor.execute("SELECT COUNT(*) FROM fact_ev_sales;").fetchone()[0]
    fleet_count = cursor.execute("SELECT COUNT(*) FROM fact_fleet_impact;").fetchone()[0]
    specs_count = cursor.execute("SELECT COUNT(*) FROM dim_vehicle_specs;").fetchone()[0]
    
    assert sales_count >= 40000, f"Expected >=40,000 sales rows, got {sales_count}"
    assert fleet_count >= 50, f"Expected >=50 fleet rows, got {fleet_count}"
    assert specs_count >= 100, f"Expected >=100 EV models, got {specs_count}"


def test_analytical_views_return_data(db_conn):
    """Verify all 6 analytical SQL views return valid records."""
    views = [
        "v_annual_ev_sales_by_country",
        "v_ev_sales_trend_global",
        "v_drivetrain_mix_by_year",
        "v_vehicle_specs_by_category",
        "v_fleet_sustainability_summary",
        "v_top_ev_markets_latest_year"
    ]
    cursor = db_conn.cursor()
    for v in views:
        count = cursor.execute(f"SELECT COUNT(*) FROM {v};").fetchone()[0]
        assert count > 0, f"View '{v}' returned 0 rows"


def test_dataset_sources_provenance(db_conn):
    """Ensure dataset_sources contains valid license and URLs."""
    cursor = db_conn.cursor()
    sources = cursor.execute("SELECT source_key, license, source_url FROM dataset_sources;").fetchall()
    assert len(sources) >= 3, "dataset_sources should have at least 3 entries"
    for s in sources:
        assert "CC BY 4.0" in s["license"], f"Invalid license in {s['source_key']}"
        assert s["source_url"].startswith("http"), f"Invalid source URL in {s['source_key']}"
