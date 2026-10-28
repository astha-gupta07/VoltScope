# VoltScope — Video Demonstration & Presentation Script
## 5–7 Minute Walkthrough for College Course Project Defense & Technical Interviews

> [!NOTE]
> This document is a structured presentation and speaking script designed to guide the recording of a 5–7 minute video walkthrough or a live college demonstration. No video recording has been claimed as executed.

---

## Presentation Metadata
- **Project Title**: VoltScope — Electric Vehicle Market Performance & Insights
- **Presenter**: Data Analytics & Engineering Student
- **Target Audience**: Academic Evaluators, Senior Technical Interviewers, BI Directors
- **Estimated Duration**: 6 minutes 15 seconds
- **Key Deliverables Demonstrated**: Python Pipelines, SQLite Relational Database, SQL Analytical Suite, Tableau Visuals & Story, Flask Web App with Embedding API v3, Automated Pytest Suite.

---

## Timed Demonstration Sequence

### [0:00 – 0:45] Minute 1: Problem Definition & Executive Overview
**Visual Screen**: Browser showing `http://127.0.0.1:5000/` (VoltScope Executive Overview page).  
**Narrator (Speaking Clearly)**:
> *"Hello everyone. Today I'm presenting VoltScope, an end-to-end data analytics system evaluating global electric vehicle market performance, powertrain transition, engineering specifications, and petroleum displacement.*  
> *The EV industry is experiencing rapid structural growth, but decision-makers frequently struggle with data mismatches—for instance, conflating sovereign sales volumes with manufacturer shares or using unreliable survey data.*  
> *VoltScope solves this by providing a unified, reproducible platform built with Python, SQLite, SQL, Tableau, and Flask. As you can see on our executive dashboard, in 2025 alone, over 14 million new electric vehicles were registered across our surveyed sovereign markets, representing an active global fleet of over 40 million units displacing 1.4 million barrels of crude oil equivalent annually."*

---

### [0:45 – 1:45] Minute 2: Data Acquisition & Rigorous Preparation
**Visual Screen**: Terminal showing `python scripts/run_pipeline.py` or VS Code showing `scripts/prepare_data.py` and `data/processed/data_quality_report.json`.  
**Narrator**:
> *"Let's look under the hood at data engineering and provenance. We ingested two primary open-source datasets under Creative Commons CC BY 4.0:*  
> *First, Ember Energy's monthly registration dataset containing over 46,500 monthly rows spanning 56 nations from 2005 to 2026, alongside national fleet and oil displacement figures.*  
> *Second, autoseeker's technical catalog, which we filtered strictly to 166 verified electrified vehicle models.*  
> *Our data preparation script standardizes schema headers, parses ISO-8601 dates, translates Dutch vehicle body categories to standard English categories like SUV, Sedan, and Hatchback, and computes derived engineering metrics like range efficiency (kilometers per kilowatt-hour).*  
> *Crucially, we maintain strict data integrity: model specifications and country sales are never improperly cross-joined, preserving authentic data grains."*

---

### [1:45 – 2:45] Minute 3: SQLite Relational Database & SQL Operations
**Visual Screen**: VS Code showing `database/schema.sql`, `database/views.sql`, or a SQLite query execution tool.  
**Narrator**:
> *"Moving to our database tier, we loaded the processed data into an optimized SQLite database with composite B-tree indexing. Our schema comprises four tables: `fact_ev_sales`, `fact_fleet_impact`, `dim_vehicle_specs`, and `dataset_sources`.*  
> *We developed six reusable SQL views to support high-performance reporting. For example, `v_annual_ev_sales_by_country` filters by `is_country = 1` to prevent double-counting regional totals like the EU and World.*  
> *Our SQL query portfolio demonstrates complex analytical techniques: Common Table Expressions (CTEs), window functions like `RANK()` and `LAG()` to compute annual sales growth trajectories, `CASE` expressions for range performance tiering, and `NULLIF()` expressions for zero-division safety when calculating per-vehicle oil displacement ratios.*  
> *Our automated benchmarks show that indexed queries execute in under 15 milliseconds."*

---

### [2:45 – 4:00] Minute 4: Tableau Analytics & 4-Scene Story
**Visual Screen**: Browser showing `http://127.0.0.1:5000/dashboard` and `http://127.0.0.1:5000/story` (or Tableau Desktop showing the workbook).  
**Narrator**:
> *"Now let's examine our Business Intelligence layer. In `data/exports/tableau/`, our pipeline generates five clean, denormalized CSV extracts designed specifically for Tableau Desktop and Tableau Public.*  
> *We designed six distinct visualizations:*  
> *1. A dual-axis line chart illustrating global monthly registrations and 12-month rolling momentum.*  
> *2. A ranked bar chart highlighting top sovereign markets in 2025, where China, the United States, Germany, and the UK lead in volume.*  
> *3. A 100% stacked area chart demonstrating powertrain transition, where pure BEVs outpace PHEVs by nearly 3 to 1.*  
> *4. A scatter plot of battery capacity versus WLTP driving range showing an empirical scaling factor of approximately 5.8 km per kWh.*  
> *5. Category benchmarks revealing that SUVs represent over 53% of all modern EV offerings, averaging 468 km of range.*  
> *6. A sustainability map showing national petroleum displacement.*  
> *Furthermore, we structured a four-scene Tableau Story: starting from the Market at a Glance, moving to Geographic Adoption, exploring Technology Trade-offs, and concluding with Strategic Recommendations tailored for our three stakeholders: Emily Johnson, David Chen, and Dr. Sarah Williams."*

---

### [4:00 – 5:00] Minute 5: Flask Presentation Layer & Tableau Embedding API v3
**Visual Screen**: Clicking through `http://127.0.0.1:5000/`, switching between `/dashboard`, `/story`, `/data`, and `/about`.  
**Narrator**:
> *"To bring this solution to production, we built a responsive Flask web application. Notice the clean, restrained visual identity—inspired by clean energy analytics using deep navy, muted teal, and crisp typography rather than generic templates.*  
> *On the technical integration side, our application implements the official Tableau Embedding API v3 using the `<tableau-viz>` web component.*  
> *When Tableau Public URLs are configured in `.env`, the live interactive workbook embeds directly. If the URLs are not yet set, our site provides a graceful local interactive preview using Chart.js powered by five live REST API endpoints.*  
> *Users can also visit `/data` to review our live data catalog, data quality report, and SQLite table statistics."*

---

### [5:00 – 6:15] Minute 6: Automated Testing & Conclusion
**Visual Screen**: Running `pytest tests/ -v` in terminal, showing 14 passed tests in ~2 seconds.  
**Narrator**:
> *"Quality assurance is fundamental to VoltScope. We implemented a comprehensive automated test suite with pytest covering data integrity, schema consistency, non-negative constraints, SQLite views, and Flask endpoints.*  
> *As you can see, all 14 unit and integration tests pass cleanly.*  
> *In conclusion, VoltScope provides a complete, explainable, and professionally structured data analytics project demonstrating full-stack competencies from data engineering and relational database design to advanced BI storytelling and web embedding.*  
> *Thank you, and I look forward to your questions!"*

---

## Anticipated Evaluator / Interview Q&A Defense

**Q1: Why did you use SQLite instead of PostgreSQL or MySQL?**  
*Answer*: SQLite provides a zero-configuration, self-contained, and cross-platform relational database that requires no external database server or credentials, making the project 100% reproducible for academic grading and GitHub cloning. Because analytical read queries execute in under 15 ms on our indexed 12.4 MB database, SQLite is performant and portable for this workload.

**Q2: Why didn't you join the vehicle specifications directly to country sales?**  
*Answer*: That would violate data grain integrity. Sales are reported at the level of Country + Month + Drivetrain, while vehicle specifications are at the model level. Joining them directly on brand would duplicate sales figures or imply that every model is sold equally across all 56 countries. Keeping them as distinct tables respects real-world automotive market reality.

**Q3: How does the Tableau embedding work if Tableau Desktop isn't installed?**  
*Answer*: VoltScope exports clean, typed CSV extracts into `data/exports/tableau/` so any user can connect in Tableau Public or Desktop. On the web side, our Flask application implements the official Tableau Embedding API v3 web component. When the workbook is published, simply pasting the public URL into `.env` renders it live; meanwhile, our built-in Chart.js preview ensures the site remains 100% functional.
