"""
VoltScope - Tableau Data Extract Exporter
Extracts structured, denormalized, analysis-ready datasets from SQLite views
and exports them to data/exports/tableau/ for Tableau Desktop & Public connections.
"""

import sys
import sqlite3
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATABASE_FILE, TABLEAU_EXPORTS_DIR


def export_tableau_extracts() -> dict:
    """Generate all Tableau-optimized CSV exports."""
    print("=" * 70)
    print(" VoltScope Tableau Data Extract Generator")
    print("=" * 70)
    
    TABLEAU_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    export_metrics = {}
    
    try:
        # 1. Market Sales Time Series Extract (Country Level)
        print("[*] Generating 'tableau_ev_market_sales.csv'...")
        q_sales = """
            SELECT 
                area AS Country,
                iso_3_code AS [ISO 3 Code],
                continent AS Continent,
                ember_region AS [Ember Region],
                date AS [Month Date],
                year AS [Year],
                month AS [Month],
                drivetrain AS [Drivetrain],
                is_aggregate_drivetrain AS [Is Aggregate Drivetrain],
                registrations AS [Registrations],
                registrations_yoy_change_pct AS [YoY Growth %],
                share_of_registrations_pct AS [Market Share %],
                rolling_12m_registrations AS [Rolling 12M Registrations]
            FROM fact_ev_sales
            WHERE is_country = 1
            ORDER BY Country, [Month Date], Drivetrain;
        """
        df_sales = pd.read_sql_query(q_sales, conn)
        out_sales = TABLEAU_EXPORTS_DIR / "tableau_ev_market_sales.csv"
        df_sales.to_csv(out_sales, index=False)
        print(f"    [+] Saved {len(df_sales):,} rows to {out_sales.name}")
        export_metrics["tableau_ev_market_sales"] = len(df_sales)

        # 2. Fleet & Sustainability Impact Extract
        print("[*] Generating 'tableau_ev_fleet_sustainability.csv'...")
        q_fleet = """
            SELECT 
                f.area AS Country,
                f.iso_3_code AS [ISO 3 Code],
                f.latest_available_date AS [Latest Date],
                f.ev_fleet_vehicles AS [EV Fleet Vehicles],
                f.electricity_demand_gwh_yr AS [Electricity Demand GWh/Yr],
                f.oil_displaced_kbd_yr AS [Oil Displaced (Thousand Bbl/Yr)],
                f.oil_displaced_usd_million_yr AS [Economic Value Displaced ($M)],
                f.brent_price_usd AS [Brent Crude Benchmark ($/bbl)],
                ROUND(f.oil_displaced_kbd_yr * 1000.0 / NULLIF(f.ev_fleet_vehicles, 0), 2) AS [Barrels Displaced Per EV/Yr]
            FROM fact_fleet_impact f
            WHERE f.is_country = 1
            ORDER BY [Oil Displaced (Thousand Bbl/Yr)] DESC;
        """
        df_fleet = pd.read_sql_query(q_fleet, conn)
        out_fleet = TABLEAU_EXPORTS_DIR / "tableau_ev_fleet_sustainability.csv"
        df_fleet.to_csv(out_fleet, index=False)
        print(f"    [+] Saved {len(df_fleet):,} rows to {out_fleet.name}")
        export_metrics["tableau_ev_fleet_sustainability"] = len(df_fleet)

        # 3. Vehicle Technical Specifications Extract
        print("[*] Generating 'tableau_vehicle_specifications.csv'...")
        q_specs = """
            SELECT 
                model_id AS [Model Slug],
                brand AS [Brand],
                model_name AS [Model Name],
                generation AS [Generation],
                body_category AS [Vehicle Category],
                drivetrain_class AS [Drivetrain Class],
                release_year AS [Release Year],
                power_hp AS [Power (HP)],
                battery_capacity_kwh AS [Battery Capacity (kWh)],
                range_wltp_km AS [WLTP Range (km)],
                efficiency_km_per_kwh AS [Efficiency (km/kWh)],
                consumption_kwh_100km AS [Consumption (kWh/100km)],
                fast_charge_dc_kw AS [DC Fast Charge Power (kW)],
                has_fast_charging AS [Has Fast Charging Flag],
                towing_capacity_kg AS [Towing Capacity (kg)],
                cargo_volume_liters AS [Cargo Volume (Liters)],
                seats AS [Seats],
                doors AS [Doors]
            FROM dim_vehicle_specs
            ORDER BY Brand, [Model Name];
        """
        df_specs = pd.read_sql_query(q_specs, conn)
        out_specs = TABLEAU_EXPORTS_DIR / "tableau_vehicle_specifications.csv"
        df_specs.to_csv(out_specs, index=False)
        print(f"    [+] Saved {len(df_specs):,} rows to {out_specs.name}")
        export_metrics["tableau_vehicle_specifications"] = len(df_specs)

        # 4. Annual Drivetrain Mix Transformation
        print("[*] Generating 'tableau_drivetrain_mix_annual.csv'...")
        q_mix = "SELECT * FROM v_drivetrain_mix_by_year ORDER BY year, drivetrain;"
        df_mix = pd.read_sql_query(q_mix, conn)
        out_mix = TABLEAU_EXPORTS_DIR / "tableau_drivetrain_mix_annual.csv"
        df_mix.to_csv(out_mix, index=False)
        print(f"    [+] Saved {len(df_mix):,} rows to {out_mix.name}")
        export_metrics["tableau_drivetrain_mix_annual"] = len(df_mix)

        # 5. Top EV Markets Summary (2025 Calendar Benchmark)
        print("[*] Generating 'tableau_top_markets_summary.csv'...")
        q_top = "SELECT * FROM v_top_ev_markets_latest_year ORDER BY annual_ev_sales DESC;"
        df_top = pd.read_sql_query(q_top, conn)
        out_top = TABLEAU_EXPORTS_DIR / "tableau_top_markets_summary.csv"
        df_top.to_csv(out_top, index=False)
        print(f"    [+] Saved {len(df_top):,} rows to {out_top.name}")
        export_metrics["tableau_top_markets_summary"] = len(df_top)

        print(f"\n[+] All 5 Tableau extracts generated successfully in {TABLEAU_EXPORTS_DIR.name}/")
        return export_metrics
    finally:
        conn.close()


if __name__ == "__main__":
    export_tableau_extracts()
