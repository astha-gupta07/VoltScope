# VoltScope — Electric Vehicle Market Performance & Insights

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Database SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Flask Web](https://img.shields.io/badge/Framework-Flask%203.1-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tableau Ready](https://img.shields.io/badge/BI-Tableau%20Embedding%20API%20v3-E97627.svg?logo=tableau&logoColor=white)](https://help.tableau.com/current/api/embedding_api/en-us/)
[![License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Tests Passing](https://img.shields.io/badge/pytest-14%20passed-success.svg)](tests/)

> **VoltScope** is an end-to-end data analytics and business intelligence platform evaluating global electric vehicle (EV) sales velocity, powertrain market share transitions, engineering specifications (battery vs range), and petroleum displacement across 56 countries and 160+ models from 2005 through 2026.

---

## ⚡ Key Highlights & Architecture

- **Real Open Datasets (CC BY 4.0)**: Ingests 46,500+ official monthly registration records from **Ember Energy** and 166 electrified vehicle models from **autoseeker.eu**.
- **Strict Data Integrity**: Segregates market sales and model specifications at authentic grains—never cross-multiplying or inventing artificial figures.
- **Relational SQLite Database**: 12.4 MB optimized database featuring composite indexing, foreign keys, and 6 analytical SQL views.
- **Advanced SQL Query Portfolio**: Includes Common Table Expressions (CTEs), window functions (`RANK()`, `LAG()`), `HAVING` filters, `CASE` expressions, and zero-division safe `NULLIF()` expressions.
- **Tableau Analytics & 4-Scene Story**: 5 pre-computed Tableau extracts, 6 core visualizations, 5 calculated fields, an executive dashboard, and a 4-scene narrative story.
- **Flask Presentation Web App**: Integrates the official **Tableau Embedding API v3** web component (`<tableau-viz>`), with seamless fallback to a native Chart.js interactive preview when public URLs are not yet configured.
- **Automated Testing & Benchmarks**: 14 automated tests with `pytest` and measured query latency under 15 ms.

---

## 📂 Project Repository Structure

```
VoltScope/
├── app.py                      # Flask presentation web application & REST APIs
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions for venvs, dbs, and caches
├── README.md                   # Project overview & documentation
│
├── config/
│   └── settings.py             # Central application configuration & paths
│
├── data/
│   ├── raw/                    # Immutable raw files from Ember & autoseeker
│   │   └── README.md           # Raw data provenance & manual download instructions
│   ├── processed/              # Cleaned datasets & data_quality_report.json
│   ├── exports/
│   │   └── tableau/            # 5 Clean Tableau-ready CSV extracts
│   │       └── README.md       # Tableau extract connection & ODBC workflow
│   └── README.md               # 3-Tier data lifecycle guide
│
├── database/
│   ├── schema.sql              # DDL schema for SQLite fact/dimension tables & indexes
│   ├── views.sql               # 6 Reusable analytical SQL views
│   ├── queries.sql             # SQL analytical query portfolio (8 complex queries)
│   └── voltscope.db            # Operational SQLite relational database (12.4 MB)
│
├── scripts/
│   ├── download_data.py        # Automated data acquisition script
│   ├── validate_data.py        # Schema, range, candidate key & anomaly validator
│   ├── prepare_data.py         # Cleaning, category normalization, and derived metrics
│   ├── load_database.py        # Database loader, view runner, and provenance logger
│   ├── export_tableau_data.py  # Tableau CSV extract generator
│   ├── benchmark_performance.py# Latency & query performance benchmarking tool
│   └── run_pipeline.py         # Master orchestration pipeline runner
│
├── templates/
│   ├── base.html               # Master layout with clean energy navigation & footer
│   ├── index.html              # Executive summary, top markets, and KPI cards
│   ├── dashboard.html          # Tableau v3 embed + local interactive BI preview
│   ├── story.html              # 4-scene narrative walkthrough + Tableau Story embed
│   ├── data.html               # Live data catalog, provenance, and SQLite preview
│   └── about.html              # Stakeholder scenarios, methodology, and limitations
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean energy BI stylesheet (Navy, Slate, Muted Teal)
│   └── js/
│       └── main.js             # Interactive Chart.js visualizations & scene handlers
│
├── docs/
│   ├── PROJECT_REPORT.md       # Comprehensive academic project report
│   ├── DATA_DICTIONARY.md      # Field definitions, grains, data types, and null rules
│   ├── SQL_GUIDE.md            # Schema design, ER diagram, view specs, and query guide
│   ├── TABLEAU_BUILD_GUIDE.md  # Detailed Tableau build guide (6 charts, 5 calcs, story)
│   ├── FLASK_INTEGRATION.md    # Tableau Embedding API v3 & REST API guide
│   ├── PERFORMANCE_REPORT.md   # Empirically measured system & query benchmarks
│   ├── VIDEO_DEMO_SCRIPT.md    # Timed 5–7 minute presentation script & Q&A defense
│   └── REQUIREMENTS_TRACEABILITY.md # Matrix mapping all 8 Epics & 14 Tasks
│
└── tests/
    ├── test_data_validation.py # Data integrity, range, and non-negative unit tests
    ├── test_database.py        # SQLite schema, foreign keys, views, and count tests
    └── test_app.py             # Flask route, template, and REST JSON API tests
```

---

## 🚀 Quickstart Guide (Windows)

### 1. Prerequisites
- **Python 3.10+** (tested on Python 3.13)
- PowerShell or Windows Command Prompt

### 2. Clone / Open Directory
```powershell
cd "c:\Users\ACER\OneDrive\Desktop\electric vehicle project"
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Master Ingestion & Analytical Pipeline
Executes data downloading, schema validation, normalization, SQLite database loading, and Tableau extract generation in one command:
```powershell
python scripts/run_pipeline.py
```

### 5. Run the Automated Test Suite
```powershell
python -m pytest tests/ -v
```
*Expected: 14 passed in ~2 seconds.*

### 6. Run System & Query Performance Benchmarks
```powershell
python scripts/benchmark_performance.py
```
*Outputs empirically measured latencies to `docs/PERFORMANCE_REPORT.md`.*

### 7. Launch the Flask Presentation Web App
```powershell
python app.py
```
Open your web browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 📊 Tableau Desktop & Public Integration

VoltScope exports 5 clean, analysis-ready CSV extracts to `data/exports/tableau/`:
1. `tableau_ev_market_sales.csv`: Time-series registrations, YoY growth, and market shares.
2. `tableau_ev_fleet_sustainability.csv`: National fleet size, electricity demand, and oil displacement.
3. `tableau_vehicle_specifications.csv`: Battery capacity, WLTP range, charging power, and efficiency.
4. `tableau_drivetrain_mix_annual.csv`: Annual powertrain breakdown (BEV, PHEV, Hybrid, ICE).
5. `tableau_top_markets_summary.csv`: 2025 calendar year benchmark leaderboard.

### Connecting in Tableau:
1. Open Tableau Desktop or Tableau Public.
2. Click **To a File** -> **Text file** -> Select `tableau_ev_market_sales.csv`.
3. Add `tableau_vehicle_specifications.csv` and `tableau_ev_fleet_sustainability.csv` as separate data sources.
4. Follow the step-by-step instructions in [TABLEAU_BUILD_GUIDE.md](docs/TABLEAU_BUILD_GUIDE.md) to build:
   - 6 Core Visualizations
   - 5 Calculated Fields (`[YoY EV Sales Growth %]`, `[EV Market Penetration %]`, `[Driving Efficiency (km/kWh)]`, etc.)
   - The Executive Dashboard
   - The 4-Scene Tableau Story
5. To embed your published Tableau Public views into the web application, copy your view URLs into `.env`:
   ```env
   TABLEAU_DASHBOARD_URL="https://public.tableau.com/views/VoltScope/ExecutiveDashboard"
   TABLEAU_STORY_URL="https://public.tableau.com/views/VoltScope/EVStory"
   ```
   *Note: If these URLs are left blank, VoltScope seamlessly displays its high-fidelity local interactive Chart.js preview.*

---

## 🎯 Target Stakeholders

1. **Emily Johnson (EV Market Strategy Director)**:
   - Uses vehicle category distributions and battery-range scatter plots to optimize portfolio planning (targeting 65–75 kWh C-segment crossovers).
2. **David Chen (Automotive Business Intelligence Manager)**:
   - Uses multi-year volume rankings and drivetrain substitution trends to guide international market entry and competitive positioning.
3. **Dr. Sarah Williams (Sustainable Mobility Research Analyst)**:
   - Uses cumulative fleet indicators and barrels of petroleum displaced to evaluate national grid power integration and transport decarbonization policies.

---

## 📜 Intellectual Property & Data Provenance

All datasets used in VoltScope are public, open-access, and governed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license:
- **Ember Energy**: Monthly EV Sales & Fleet Impact Data ([Source & Methodology](https://ember-energy.org/data/monthly-ev-sales-data/)).
- **autoseeker.eu**: Open Car Technical Specifications by Dennis de Kruijf ([Source & Data](https://autoseeker.eu/en/data/)).
- **Zero Synthetic Records**: Real data only. No fake customer ratings or invented sales numbers.

---

## 🎓 Academic Deliverables Reference

- [Project Report](docs/PROJECT_REPORT.md) — Comprehensive academic research paper.
- [GitHub & Cloud Deployment Guide](docs/GITHUB_AND_DEPLOYMENT_GUIDE.md) — Step-by-step GitHub setup and Render cloud deployment.
- [Data Dictionary](docs/DATA_DICTIONARY.md) — Granular field definitions, types, and null rules.
- [SQL Guide](docs/SQL_GUIDE.md) — Relational schema, ER diagram, and query portfolio.
- [Tableau Build Guide](docs/TABLEAU_BUILD_GUIDE.md) — Step-by-step Tableau worksheet and story construction manual.
- [Flask Integration](docs/FLASK_INTEGRATION.md) — Embedding API v3 and local preview architecture.
- [Performance Report](docs/PERFORMANCE_REPORT.md) — Empirically measured hardware, database, and query benchmarks.
- [Video Demo Script](docs/VIDEO_DEMO_SCRIPT.md) — Word-for-word 5–7 minute presentation script & defense.
- [Requirements Traceability](docs/REQUIREMENTS_TRACEABILITY.md) — Complete 8-Epic & 14-Task compliance matrix.
