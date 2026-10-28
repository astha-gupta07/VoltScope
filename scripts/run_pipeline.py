"""
VoltScope - Master Orchestration Pipeline
Executes end-to-end data acquisition, validation, transformation,
database ingestion, and Tableau export generation in one reproducible workflow.
"""

import sys
import time
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.download_data import run_download
from scripts.validate_data import run_validation
from scripts.prepare_data import run_preparation
from scripts.load_database import run_loader
from scripts.export_tableau_data import export_tableau_extracts


def run_full_pipeline(force_download: bool = False) -> dict:
    """Execute the 5 core stages of the VoltScope data pipeline."""
    start_time = time.time()
    
    print("\n" + "=" * 76)
    print("  VOLTSCOPE DATA ANALYTICS PIPELINE — END-TO-END EXECUTION")
    print("=" * 76 + "\n")
    
    # Stage 1: Download
    print(">> [STAGE 1/5] Ingesting Raw Datasets...")
    download_stats = run_download(force=force_download)
    
    # Stage 2: Validation
    print("\n>> [STAGE 2/5] Validating Raw Schemas & Constraints...")
    validation_stats = run_validation()
    if not validation_stats.get("overall_passed", False):
        print("\n[!] Pipeline halted: Data validation checks failed.")
        sys.exit(1)
        
    # Stage 3: Preparation
    print("\n>> [STAGE 3/5] Cleaning, Normalizing & Computing Derived Metrics...")
    prep_stats = run_preparation()
    
    # Stage 4: Database Ingestion
    print("\n>> [STAGE 4/5] Initializing SQLite Schema, Views & Ingesting Records...")
    db_stats = run_loader()
    
    # Stage 5: Tableau Exports
    print("\n>> [STAGE 5/5] Generating Tableau-Ready CSV Extracts...")
    tableau_stats = export_tableau_extracts()
    
    total_elapsed = round(time.time() - start_time, 2)
    
    print("\n" + "=" * 76)
    print("  VOLTSCOPE PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 76)
    print(f"Total Execution Time   : {total_elapsed}s")
    print(f"Fact EV Sales Records  : {db_stats.get('fact_ev_sales', 0):,}")
    print(f"Fact Fleet Records     : {db_stats.get('fact_fleet_impact', 0):,}")
    print(f"Vehicle Spec Models    : {db_stats.get('dim_vehicle_specs', 0):,}")
    print(f"SQLite DB File Size    : {db_stats.get('database_size_mb', 0)} MB")
    print(f"Tableau Extracts Ready : {len(tableau_stats)} files in data/exports/tableau/")
    print("=" * 76 + "\n")
    
    return {
        "status": "success",
        "total_elapsed_sec": total_elapsed,
        "database_stats": db_stats,
        "tableau_stats": tableau_stats
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VoltScope Master Orchestration Pipeline")
    parser.add_argument("--force", action="store_true", help="Force re-download of raw datasets.")
    args = parser.parse_args()
    
    run_full_pipeline(force_download=args.force)
