# Tableau Connection & Extract Workflow Guide

This directory contains pre-processed, denormalized, and strongly-typed CSV data extracts generated specifically for **Tableau Desktop** and **Tableau Public**.

## Available Tableau Extracts

| Extract Filename | Grain | Key Dimensions | Key Measures | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `tableau_ev_market_sales.csv` | Country + Month + Drivetrain | `Country`, `ISO 3 Code`, `Continent`, `Month Date`, `Year`, `Drivetrain` | `Registrations`, `YoY Growth %`, `Market Share %`, `Rolling 12M Registrations` | Time-series trends, adoption curves, country rankings |
| `tableau_ev_fleet_sustainability.csv` | Country | `Country`, `ISO 3 Code`, `Latest Date` | `EV Fleet Vehicles`, `Electricity Demand GWh/Yr`, `Oil Displaced`, `Economic Value Displaced` | Environmental sustainability, oil displacement map |
| `tableau_vehicle_specifications.csv` | Vehicle Model Slug | `Brand`, `Model Name`, `Vehicle Category`, `Drivetrain Class` | `Battery Capacity (kWh)`, `WLTP Range (km)`, `Efficiency (km/kWh)`, `DC Fast Charge Power (kW)` | Engineering scatter plots, battery vs range, category boxplots |
| `tableau_drivetrain_mix_annual.csv` | Year + Drivetrain | `Year`, `Drivetrain` | `Total Registrations`, `Avg Share %` | 100% Stacked bar / area chart of ICE vs EV transition |
| `tableau_top_markets_summary.csv` | Country | `Country`, `ISO 3 Code`, `Continent` | `Annual EV Sales`, `Avg Market Share %` | Executive KPI leaderboard, top 10 market bar chart |

---

## Step-by-Step Connection Instructions

### Option A: Direct CSV / Text File Connection (Recommended & Universally Supported)
This method is 100% compatible with both **Tableau Desktop** and **Tableau Public** (free version) without requiring ODBC drivers:

1. **Launch Tableau**: Open Tableau Desktop or Tableau Public.
2. **Connect to Data**: Under the **To a File** pane on the left, click **Text file**.
3. **Select Extract**: Navigate to `VoltScope/data/exports/tableau/` and select `tableau_ev_market_sales.csv`.
4. **Inspect Data Source**:
   - Verify that `Month Date` is recognized as a **Date** type (`#` calendar icon).
   - Verify that `Country` is recognized as a **Geographic Role** -> **Country/Region**.
   - Verify that `Registrations` is recognized as a **Measure** (green number `#`).
5. **Add Secondary Data Sources**:
   - In Tableau, click **Data** -> **New Data Source** -> **Text file**.
   - Add `tableau_vehicle_specifications.csv` and `tableau_ev_fleet_sustainability.csv` as independent, separate data sources.
   - *Note on Data Integrity*: Do not join `tableau_vehicle_specifications.csv` to `tableau_ev_market_sales.csv` directly on Brand or Country; maintain them as separate data sources to avoid inflating sales figures.
6. **Open Worksheet**: Click **Sheet 1** at the bottom to begin building the visualizations.

---

### Option B: Direct SQLite Database Connection (Tableau Desktop with SQLite ODBC)
If you are using Tableau Desktop on Windows and wish to query `database/voltscope.db` directly:

1. **Install SQLite ODBC Driver**:
   - Download the 64-bit SQLite ODBC driver installer (`sqliteodbc_w64.exe`) from `http://www.ch-werner.de/sqliteodbc/`.
   - Run the installer with administrative privileges.
2. **Configure Windows DSN**:
   - Open **ODBC Data Source Administrator (64-bit)** in Windows.
   - Click the **System DSN** tab -> **Add...** -> Select **SQLite3 ODBC Driver**.
   - Data Source Name: `VoltScope_EV_DB`
   - Database Name: Browse to `C:\...\VoltScope\database\voltscope.db`.
   - Click **OK**.
3. **Connect in Tableau Desktop**:
   - Under **To a Server**, click **More...** -> **Other Databases (ODBC)**.
   - Select DSN: `VoltScope_EV_DB` -> Click **Connect**.
   - In the Data Source canvas, you can drag and drop any of the pre-computed SQL views:
     - `v_annual_ev_sales_by_country`
     - `v_ev_sales_trend_global`
     - `v_drivetrain_mix_by_year`
     - `v_vehicle_specs_by_category`
     - `v_fleet_sustainability_summary`
     - `v_top_ev_markets_latest_year`
