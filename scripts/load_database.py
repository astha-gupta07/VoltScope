"""
VoltScope - Database Initialization & Ingestion Loader
Executes SQLite DDL schema, views, registers dataset sources,
and loads cleaned datasets into relational tables.
"""

import sys
import sqlite3
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import (
    DATABASE_FILE, SCHEMA_FILE, VIEWS_FILE, QUERIES_FILE,
    PROCESSED_DATA_DIR, DATASET_SOURCES
)


def init_database() -> sqlite3.Connection:
    """Initialize SQLite database with schema and views."""
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    print(f"[*] Initializing SQLite database at: {DATABASE_FILE}")
    
    # 1. Execute Schema DDL
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print("    [+] Schema tables and indexes created successfully.")
    
    # 2. Execute Views DDL
    with open(VIEWS_FILE, "r", encoding="utf-8") as f:
        views_sql = f.read()
    conn.executescript(views_sql)
    print("    [+] Analytical SQL views created successfully.")
    
    return conn


def register_dataset_sources(conn: sqlite3.Connection, sources_metadata: dict):
    """Insert provenance metadata into dataset_sources table."""
    cursor = conn.cursor()
    retrieval_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    
    for key, info in DATASET_SOURCES.items():
        count = sources_metadata.get(key, {}).get("records", 0)
        cursor.execute("""
            INSERT INTO dataset_sources (
                source_key, source_name, publisher, source_url, license, retrieval_date, record_count, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_key) DO UPDATE SET
                retrieval_date = excluded.retrieval_date,
                record_count = excluded.record_count;
        """, (
            key,
            info["name"],
            info["publisher"],
            info["url"],
            info["license"],
            retrieval_date,
            count,
            info["description"]
        ))
    conn.commit()
    print("    [+] Dataset provenance registered in 'dataset_sources'.")


def load_data(conn: sqlite3.Connection) -> dict:
    """Load cleaned CSVs into SQLite tables."""
    stats = {}
    
    # 1. Load Fact EV Sales
    sales_file = PROCESSED_DATA_DIR / "cleaned_ev_sales.csv"
    if sales_file.exists():
        print(f"[*] Loading {sales_file.name} into 'fact_ev_sales'...")
        df_sales = pd.read_csv(sales_file)
        # Clear existing
        conn.execute("DELETE FROM fact_ev_sales;")
        df_sales.to_sql("fact_ev_sales", conn, if_exists="append", index=False, chunksize=5000)
        count = conn.execute("SELECT COUNT(*) FROM fact_ev_sales;").fetchone()[0]
        print(f"    [+] Loaded {count:,} rows into fact_ev_sales.")
        stats["fact_ev_sales"] = count
        
    # 2. Load Fact Fleet Impact
    fleet_file = PROCESSED_DATA_DIR / "cleaned_fleet_impact.csv"
    if fleet_file.exists():
        print(f"[*] Loading {fleet_file.name} into 'fact_fleet_impact'...")
        df_fleet = pd.read_csv(fleet_file)
        conn.execute("DELETE FROM fact_fleet_impact;")
        df_fleet.to_sql("fact_fleet_impact", conn, if_exists="append", index=False)
        count = conn.execute("SELECT COUNT(*) FROM fact_fleet_impact;").fetchone()[0]
        print(f"    [+] Loaded {count:,} rows into fact_fleet_impact.")
        stats["fact_fleet_impact"] = count
        
    # 3. Load Dimension Vehicle Specs
    specs_file = PROCESSED_DATA_DIR / "cleaned_vehicle_specs.csv"
    if specs_file.exists():
        print(f"[*] Loading {specs_file.name} into 'dim_vehicle_specs'...")
        df_specs = pd.read_csv(specs_file)
        conn.execute("DELETE FROM dim_vehicle_specs;")
        df_specs.to_sql("dim_vehicle_specs", conn, if_exists="append", index=False)
        count = conn.execute("SELECT COUNT(*) FROM dim_vehicle_specs;").fetchone()[0]
        print(f"    [+] Loaded {count:,} rows into dim_vehicle_specs.")
        stats["dim_vehicle_specs"] = count
        
    # Register sources
    sources_meta = {
        "ember_monthly_sales": {"records": stats.get("fact_ev_sales", 0)},
        "ember_fleet_impact": {"records": stats.get("fact_fleet_impact", 0)},
        "autoseeker_models": {"records": stats.get("dim_vehicle_specs", 0)}
    }
    register_dataset_sources(conn, sources_meta)
    
    return stats


def test_views(conn: sqlite3.Connection):
    """Verify all SQL views execute cleanly and return records."""
    views = [
        "v_annual_ev_sales_by_country",
        "v_ev_sales_trend_global",
        "v_drivetrain_mix_by_year",
        "v_vehicle_specs_by_category",
        "v_fleet_sustainability_summary",
        "v_top_ev_markets_latest_year"
    ]
    print("\n[*] Testing analytical views...")
    for v in views:
        res = conn.execute(f"SELECT COUNT(*) FROM {v};").fetchone()[0]
        print(f"    [+] View '{v}': {res:,} rows returned")


def run_loader() -> dict:
    """Execute complete database setup and data ingestion."""
    print("=" * 70)
    print(" VoltScope SQLite Ingestion & Loader")
    print("=" * 70)
    
    conn = init_database()
    try:
        stats = load_data(conn)
        test_views(conn)
        
        db_size_mb = DATABASE_FILE.stat().st_size / (1024 * 1024)
        print(f"\n[+] SQLite database operational: {DATABASE_FILE.name} ({db_size_mb:.2f} MB)")
        stats["database_size_mb"] = round(db_size_mb, 2)
        return stats
    finally:
        conn.close()


if __name__ == "__main__":
    run_loader()
