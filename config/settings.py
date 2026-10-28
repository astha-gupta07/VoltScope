"""
VoltScope - Configuration & Environment Settings
Centralizes directory paths, database URLs, Tableau embedding parameters,
and external dataset sources for reproducible data ingestion and serving.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Subdirectories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
TABLEAU_EXPORTS_DIR = EXPORTS_DIR / "tableau"
DATABASE_DIR = BASE_DIR / "database"
DOCS_DIR = BASE_DIR / "docs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Database Configuration
DATABASE_FILE = DATABASE_DIR / "voltscope.db"
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
VIEWS_FILE = DATABASE_DIR / "views.sql"
QUERIES_FILE = DATABASE_DIR / "queries.sql"

# Flask Application Settings
SECRET_KEY = os.getenv("SECRET_KEY", "voltscope-default-dev-secret-key-2026")
DEBUG = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
PORT = int(os.getenv("PORT", "5000"))

# Tableau Embedding Configuration (Embedding API v3)
# If empty or None, Flask template displays the native interactive local preview
TABLEAU_DASHBOARD_URL = os.getenv("TABLEAU_DASHBOARD_URL", "").strip()
TABLEAU_STORY_URL = os.getenv("TABLEAU_STORY_URL", "").strip()

# Authoritative Dataset Sources & Provenance Metadata
DATASET_SOURCES = {
    "ember_monthly_sales": {
        "name": "Ember Monthly EV Sales Data",
        "publisher": "Ember (Global Energy Think Tank)",
        "url": "https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/transport/outputs/monthly_ev_sales.csv",
        "source_page": "https://ember-energy.org/data/monthly-ev-sales-data/",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "local_file": RAW_DATA_DIR / "monthly_ev_sales.csv",
        "description": "Monthly new electric car registrations across 56 countries, the EU, and World by drivetrain."
    },
    "ember_fleet_impact": {
        "name": "Ember EV Fleet & Oil Displacement Impact",
        "publisher": "Ember (Global Energy Think Tank)",
        "url": "https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/transport/outputs/monthly_ev_fleet_impact.csv",
        "source_page": "https://ember-energy.org/data/monthly-ev-sales-data/",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "local_file": RAW_DATA_DIR / "monthly_ev_fleet_impact.csv",
        "description": "Estimates of national and regional EV fleet size, electricity demand (GWh/yr), and barrels of oil displaced."
    },
    "autoseeker_models": {
        "name": "autoseeker Open Car Specifications",
        "publisher": "autoseeker.eu (Dennis de Kruijf)",
        "url": "https://autoseeker.eu/data/models.csv",
        "source_page": "https://autoseeker.eu/en/data/",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "local_file": RAW_DATA_DIR / "autoseeker_models.csv",
        "description": "Technical specifications for EV/PHEV passenger vehicle models (battery kWh, range km, DC charging kW, body style)."
    }
}
