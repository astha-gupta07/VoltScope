# VoltScope — Requirements Traceability Matrix
## Mapping of 8 Epics & 14 Tasks to Technical Implementation

This traceability matrix maps all requirements from the project master prompt across the 8 Epics and 14 Tasks, detailing their implementation status, corresponding code files, documentation, and verification evidence.

---

| Epic | Task # | Task Description | Status | Implementing Artifacts & Code Files | Verification Evidence / Method |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Epic 1: Problem Understanding** | **Task 1** | Define business problem, target stakeholders (Emily Johnson, David Chen, Dr. Sarah Williams), objectives, and measurable KPIs. | **COMPLETED** | `docs/PROJECT_REPORT.md`<br>`templates/about.html`<br>`templates/index.html` | Problem statement, 3 personas, and 6 measurable KPIs documented in report and live web pages. |
| | **Task 2** | Document project scope, requirements, assumptions, data integrity guardrails, and limitations. | **COMPLETED** | `docs/PROJECT_REPORT.md` (Sec. 3 & 6)<br>`templates/about.html` | Strict boundaries established: grain separation, no fake survey ratings, no HQ conflation. |
| **Epic 2: Data Collection** | **Task 3** | Identify, download, and document authoritative public datasets (Ember Energy, autoseeker.eu, CC BY 4.0). | **COMPLETED** | `scripts/download_data.py`<br>`data/raw/README.md`<br>`config/settings.py` | Programmatic downloading of 46,940 raw records. Ingestion verified in automated logs. |
| | **Task 4** | Validate raw files, source fields, candidate keys, and data quality. | **COMPLETED** | `scripts/validate_data.py`<br>`data/processed/validation_report.json` | 100% schema validation, non-negative range checks, and natural key deduplication. |
| **Epic 3: Database and SQL** | **Task 5** | Design relational SQLite schema (`fact_ev_sales`, `fact_fleet_impact`, `dim_vehicle_specs`, `dataset_sources`) and load data. | **COMPLETED** | `database/schema.sql`<br>`scripts/load_database.py`<br>`database/voltscope.db` | SQLite database created (12.44 MB) with foreign keys and 5 B-tree indexes. |
| | **Task 6** | Implement and execute 8 SQL analytical queries and 6 analytical views. | **COMPLETED** | `database/queries.sql`<br>`database/views.sql`<br>`docs/SQL_GUIDE.md` | All 8 queries (CTEs, Window Functions, HAVING, CASE, NULLIF) executed and verified. |
| **Epic 4: Data Preparation** | **Task 7** | Clean, normalize, validate, handle nulls, and compute derived engineering metrics. | **COMPLETED** | `scripts/prepare_data.py`<br>`data/processed/cleaned_ev_sales.csv`<br>`data/processed/cleaned_vehicle_specs.csv` | English category normalization, ISO dates, range efficiency ($km/kWh$), and data quality audit report. |
| **Epic 5: Tableau Analytics** | **Task 8** | Generate 5 clean Tableau extracts, design 6 visualizations, and define 5 calculated fields. | **COMPLETED** | `scripts/export_tableau_data.py`<br>`data/exports/tableau/`<br>`docs/TABLEAU_BUILD_GUIDE.md` | 5 Tableau-ready CSVs generated; formulas, data types, and chart instructions fully documented. |
| **Epic 6: Dashboard and Story** | **Task 9** | Design the interactive executive dashboard layout and responsive mobile preview. | **COMPLETED** | `templates/dashboard.html`<br>`static/js/main.js`<br>`docs/TABLEAU_BUILD_GUIDE.md` | Executive dashboard with Header, KPI row, 6 charts, interactive filters, and phone layout guide. |
| | **Task 10** | Create and document the 4-Scene Tableau Story narrative. | **COMPLETED** | `templates/story.html`<br>`static/js/main.js`<br>`docs/TABLEAU_BUILD_GUIDE.md` | 4 scenes: Market at a Glance, Where Adoption Surges, Tech & Performance, Strategic Insights. |
| **Epic 7: Testing and Web Integration** | **Task 11** | Perform performance latency benchmarks and functional testing. | **COMPLETED** | `scripts/benchmark_performance.py`<br>`docs/PERFORMANCE_REPORT.md`<br>`tests/` | Benchmarked: Ingestion, 6 queries (<15ms avg), DB size (12.4 MB). 14 automated pytest tests passing. |
| | **Task 12** | Build Flask web application and integrate Tableau Embedding API v3 with local preview fallback. | **COMPLETED** | `app.py`<br>`templates/`<br>`static/`<br>`docs/FLASK_INTEGRATION.md` | Flask app with official `<tableau-viz>` web component, 5 HTML routes, 5 REST APIs, and Chart.js fallback. |
| **Epic 8: Documentation & Demo** | **Task 13** | Complete end-to-end documentation suite. | **COMPLETED** | `README.md`<br>`docs/PROJECT_REPORT.md`<br>`docs/DATA_DICTIONARY.md`<br>`docs/SQL_GUIDE.md`<br>`docs/TABLEAU_BUILD_GUIDE.md`<br>`docs/FLASK_INTEGRATION.md`<br>`docs/PERFORMANCE_REPORT.md` | Complete documentation suite covering all academic and developer guidelines. |
| | **Task 14** | Prepare practical demonstration video script and final evidence checklist. | **COMPLETED** | `docs/VIDEO_DEMO_SCRIPT.md`<br>`docs/REQUIREMENTS_TRACEABILITY.md` | Timed 5–7 minute walkthrough script organized by minute, visual screen cue, narration, and Q&A defense. |

---

## Technical Audit Verification Checklist

- [x] **Zero Invented Data**: Raw sales, vehicle specs, and fleet numbers are directly derived from Ember Energy and autoseeker.eu.
- [x] **No Cross-Multiplying Grain Violations**: `fact_ev_sales` and `dim_vehicle_specs` remain segregated.
- [x] **Repeatable Pipelines**: `python scripts/run_pipeline.py` executes all 5 stages idempotently in ~10 seconds.
- [x] **Real Empirical Benchmarks**: Database and query benchmarks were measured and logged in `docs/PERFORMANCE_REPORT.md`.
- [x] **100% Automated Test Pass Rate**: 14 tests across `test_data_validation.py`, `test_database.py`, and `test_app.py` pass cleanly in ~2 seconds.
- [x] **Tableau Embedding API v3 Compliance**: Uses official Salesforce `<tableau-viz>` web component, with transparent local interactive fallback.
- [x] **Cross-Platform & Windows Compatibility**: Validated on Windows 11 with Python 3.13.
