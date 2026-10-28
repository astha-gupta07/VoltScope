"""
VoltScope — Electric Vehicle Market Performance & Insights
Flask Presentation Layer and Tableau Embedding Web Application
Serves analytical views, data provenance, API endpoints, and embeds
Tableau Dashboards and Stories via the official Tableau Embedding API v3.
"""

import sys
import sqlite3
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    DATABASE_FILE, TABLEAU_DASHBOARD_URL, TABLEAU_STORY_URL,
    SECRET_KEY, PORT, DEBUG, DATASET_SOURCES, PROCESSED_DATA_DIR
)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


def get_db_connection() -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database."""
    if not Path(DATABASE_FILE).exists():
        raise RuntimeError(
            f"Database not found at {DATABASE_FILE}. "
            "Run: python scripts/run_pipeline.py"
        )
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.context_processor
def inject_global_settings():
    """Inject configuration and Tableau embed parameters into all templates."""
    return {
        "tableau_dashboard_url": TABLEAU_DASHBOARD_URL,
        "tableau_story_url": TABLEAU_STORY_URL,
        "has_tableau_dashboard": bool(TABLEAU_DASHBOARD_URL),
        "has_tableau_story": bool(TABLEAU_STORY_URL)
    }


# ==============================================================================
# HTML Page Routes
# ==============================================================================

@app.route("/")
def index():
    """Home / Executive Summary page with high-level KPIs and findings."""
    # Default empty KPIs shown if database not yet built
    kpi_data = {
        "total_ev_sales_2025": 0,
        "global_fleet_vehicles": 0,
        "oil_displaced_barrels_yr": 0,
        "economic_value_usd_m": 0,
        "avg_range_km": 0,
        "avg_battery_kwh": 0,
        "avg_efficiency_km_kwh": 0,
        "countries_covered": 0
    }
    top_markets = []
    db_ready = False

    try:
        conn = get_db_connection()
        try:
            global_fleet = conn.execute(
                "SELECT ev_fleet_vehicles, oil_displaced_kbd_yr, oil_displaced_usd_million_yr FROM fact_fleet_impact WHERE area = 'World';"
            ).fetchone()

            latest_sales = conn.execute(
                "SELECT SUM(registrations) FROM fact_ev_sales WHERE is_country = 1 AND year = 2025 AND drivetrain = 'Electric vehicle (BEV+PHEV)';"
            ).fetchone()[0] or 0

            avg_specs = conn.execute(
                "SELECT AVG(range_wltp_km), AVG(battery_capacity_kwh), AVG(efficiency_km_per_kwh) FROM dim_vehicle_specs WHERE range_wltp_km > 0;"
            ).fetchone()

            countries_count = conn.execute(
                "SELECT COUNT(DISTINCT area) FROM fact_ev_sales WHERE is_country = 1;"
            ).fetchone()[0] or 0

            top_markets = conn.execute(
                "SELECT country, annual_ev_sales, avg_market_share_pct FROM v_top_ev_markets_latest_year LIMIT 5;"
            ).fetchall()

            kpi_data = {
                "total_ev_sales_2025": round(latest_sales),
                "global_fleet_vehicles": round(global_fleet["ev_fleet_vehicles"]) if global_fleet else 0,
                "oil_displaced_barrels_yr": round(global_fleet["oil_displaced_kbd_yr"] * 1000) if global_fleet else 0,
                "economic_value_usd_m": round(global_fleet["oil_displaced_usd_million_yr"]) if global_fleet else 0,
                "avg_range_km": round(avg_specs[0], 1) if avg_specs[0] else 0,
                "avg_battery_kwh": round(avg_specs[1], 1) if avg_specs[1] else 0,
                "avg_efficiency_km_kwh": round(avg_specs[2], 2) if avg_specs[2] else 0,
                "countries_covered": countries_count
            }
            db_ready = True
        finally:
            conn.close()
    except Exception as e:
        app.logger.warning(f"Database not ready, serving empty KPIs: {e}")

    return render_template("index.html", kpis=kpi_data, top_markets=top_markets, db_ready=db_ready)


@app.route("/dashboard")
def dashboard():
    """Interactive Executive Dashboard page (Tableau embed with local preview fallback)."""
    return render_template("dashboard.html")


@app.route("/story")
def story():
    """Tableau Story page (4-scene data narrative walkthrough)."""
    return render_template("story.html")


@app.route("/data")
def data_catalog():
    """Dataset catalog, data quality report, and SQLite database explorer."""
    sources = []
    dq_report = {}
    table_counts = {"fact_ev_sales": 0, "fact_fleet_impact": 0, "dim_vehicle_specs": 0}
    sample_sales = []
    sample_specs = []
    db_ready = False

    try:
        conn = get_db_connection()
        try:
            sources = conn.execute("SELECT * FROM dataset_sources ORDER BY source_key;").fetchall()

            # Load data quality report if exists
            dq_file = PROCESSED_DATA_DIR / "data_quality_report.json"
            if dq_file.exists():
                with open(dq_file, "r", encoding="utf-8") as f:
                    dq_report = json.load(f)

            # Table stats
            table_counts = {
                "fact_ev_sales": conn.execute("SELECT COUNT(*) FROM fact_ev_sales;").fetchone()[0],
                "fact_fleet_impact": conn.execute("SELECT COUNT(*) FROM fact_fleet_impact;").fetchone()[0],
                "dim_vehicle_specs": conn.execute("SELECT COUNT(*) FROM dim_vehicle_specs;").fetchone()[0]
            }

            # Sample records from fact_ev_sales
            sample_sales = conn.execute(
                "SELECT area, date, drivetrain, registrations, share_of_registrations_pct FROM fact_ev_sales WHERE is_country = 1 ORDER BY date DESC, registrations DESC LIMIT 10;"
            ).fetchall()

            # Sample records from dim_vehicle_specs
            sample_specs = conn.execute(
                "SELECT brand, model_name, body_category, battery_capacity_kwh, range_wltp_km, fast_charge_dc_kw, efficiency_km_per_kwh FROM dim_vehicle_specs WHERE range_wltp_km > 0 ORDER BY range_wltp_km DESC LIMIT 10;"
            ).fetchall()

            db_ready = True
        finally:
            conn.close()
    except Exception as e:
        app.logger.warning(f"Database not ready for /data page: {e}")

    return render_template(
        "data.html",
        sources=sources,
        dq_report=dq_report,
        table_counts=table_counts,
        sample_sales=sample_sales,
        sample_specs=sample_specs,
        db_ready=db_ready
    )


@app.route("/about")
def about():
    """Project documentation, target stakeholder scenarios, methodology, and limitations."""
    return render_template("about.html")


# ==============================================================================
# REST API Endpoints for Local Interactive Charts
# ==============================================================================

@app.route("/api/sales-trend")
def api_sales_trend():
    """Return historical global EV adoption trajectory."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT date, global_registrations AS registrations, yoy_growth_pct, rolling_12m_registrations
            FROM v_ev_sales_trend_global
            WHERE drivetrain = 'Electric vehicle (BEV+PHEV)'
              AND date >= '2015-01-01'
            ORDER BY date ASC;
        """).fetchall()
        
        data = [{
            "date": r["date"],
            "registrations": r["registrations"],
            "yoy_growth_pct": r["yoy_growth_pct"],
            "rolling_12m_registrations": r["rolling_12m_registrations"]
        } for r in rows]
        return jsonify(data)
    finally:
        conn.close()


@app.route("/api/drivetrain-mix")
def api_drivetrain_mix():
    """Return annual registrations breakdown across drivetrains."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT year, drivetrain, total_registrations, avg_share_pct
            FROM v_drivetrain_mix_by_year
            WHERE year >= 2018
            ORDER BY year ASC, total_registrations DESC;
        """).fetchall()
        
        data = [{
            "year": r["year"],
            "drivetrain": r["drivetrain"],
            "registrations": r["total_registrations"],
            "share_pct": r["avg_share_pct"]
        } for r in rows]
        return jsonify(data)
    finally:
        conn.close()


@app.route("/api/specs-by-category")
def api_specs_by_category():
    """Return vehicle specifications benchmarked by body category."""
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM v_vehicle_specs_by_category ORDER BY total_models DESC;").fetchall()
        data = [{
            "body_category": r["body_category"],
            "total_models": r["total_models"],
            "avg_range_km": r["avg_range_km"],
            "avg_battery_kwh": r["avg_battery_kwh"],
            "avg_fast_charge_dc_kw": r["avg_fast_charge_dc_kw"],
            "avg_efficiency_km_per_kwh": r["avg_efficiency_km_per_kwh"]
        } for r in rows]
        return jsonify(data)
    finally:
        conn.close()


@app.route("/api/top-countries")
def api_top_countries():
    """Return top 15 EV markets in the latest full calendar year (2025)."""
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM v_top_ev_markets_latest_year LIMIT 15;").fetchall()
        data = [{
            "country": r["country"],
            "iso_3_code": r["iso_3_code"],
            "continent": r["continent"],
            "annual_ev_sales": r["annual_ev_sales"],
            "avg_market_share_pct": r["avg_market_share_pct"]
        } for r in rows]
        return jsonify(data)
    finally:
        conn.close()


@app.route("/api/sustainability")
def api_sustainability():
    """Return top nations by barrels of oil displaced annually."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT country, iso_3_code, ev_fleet_vehicles, oil_displaced_kbd_yr,
                   oil_displaced_usd_million_yr, barrels_displaced_per_ev_yr
            FROM v_fleet_sustainability_summary
            LIMIT 15;
        """).fetchall()
        data = [{
            "country": r["country"],
            "iso_3_code": r["iso_3_code"],
            "fleet_size": r["ev_fleet_vehicles"],
            "oil_displaced_thousand_bbl": r["oil_displaced_kbd_yr"],
            "value_usd_million": r["oil_displaced_usd_million_yr"],
            "barrels_per_ev_yr": r["barrels_displaced_per_ev_yr"]
        } for r in rows]
        return jsonify(data)
    finally:
        conn.close()


if __name__ == "__main__":
    print(f"[*] Starting VoltScope Web Server on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
