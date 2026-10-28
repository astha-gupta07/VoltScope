# VoltScope — Flask & Tableau Embedding API v3 Integration Guide

This guide explains the architecture of the Flask presentation layer, the configuration of the official **Tableau Embedding API v3**, and the local development workflow.

---

## 1. Web Architecture Overview

VoltScope utilizes Flask as a lightweight, secure presentation layer bridging the SQLite analytical database and Tableau Public embeds:

- **Framework**: Flask 3.1.3 (Python 3.13)
- **Templating**: Jinja2 with semantic HTML5
- **Visual Styling**: Custom clean-energy CSS stylesheet (`static/css/style.css`)
- **Interactive Visuals**: Official Tableau Embedding API v3 (`<tableau-viz>`) + Chart.js 4.4.1 local preview fallback
- **REST APIs**: 5 JSON endpoints querying SQLite views for real-time dashboard data

---

## 2. Tableau Embedding API v3 Implementation

VoltScope implements the modern **Tableau Embedding API v3** as recommended by Salesforce/Tableau:

### A. Library Inclusion in `templates/base.html`
```html
<script type="module" src="https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js"></script>
```

### B. Custom Web Component in `templates/dashboard.html`
```html
<tableau-viz id="tableauViz" 
             src="{{ tableau_dashboard_url }}" 
             toolbar="bottom" 
             hide-tabs 
             width="100%" 
             height="850px">
</tableau-viz>
```

### C. Environmental Configuration (.env)
The URLs for published Tableau views are managed through environment variables loaded via `python-dotenv`:
```env
# In .env:
TABLEAU_DASHBOARD_URL=https://public.tableau.com/views/VoltScope_EV_Analytics/ExecutiveDashboard
TABLEAU_STORY_URL=https://public.tableau.com/views/VoltScope_EV_Analytics/EVStory
```

### D. Graceful Local Fallback Behavior
When `TABLEAU_DASHBOARD_URL` is unset or empty:
1. `app.py` passes `has_tableau_dashboard = False` to the template.
2. `dashboard.html` displays an informative configuration notice informing the user that the live embed URL has not yet been set.
3. The page automatically renders the **Native Interactive BI Preview** powered by Chart.js, fetching live verified data from `/api/sales-trend`, `/api/drivetrain-mix`, `/api/top-countries`, and `/api/specs-by-category`.
4. This ensures that the web application is 100% functional, responsive, and demonstrable even before the student or evaluator publishes a workbook to Tableau Public!

---

## 3. REST API Specifications

| Endpoint | HTTP Method | Source View / Query | Return Payload |
| :--- | :--- | :--- | :--- |
| `/api/sales-trend` | `GET` | `v_ev_sales_trend_global` | JSON array of monthly global registrations and 12-month moving averages from 2015 to 2026. |
| `/api/drivetrain-mix` | `GET` | `v_drivetrain_mix_by_year` | JSON array of annual market share % across BEV, PHEV, Hybrid, Petrol, and Diesel. |
| `/api/top-countries` | `GET` | `v_top_ev_markets_latest_year`| JSON array of top 15 sovereign nations ranked by 2025 electric registrations. |
| `/api/specs-by-category`| `GET` | `v_vehicle_specs_by_category`| JSON array of body category benchmarks (average battery kWh, range km, DC charging kW). |
| `/api/sustainability` | `GET` | `v_fleet_sustainability_summary`| JSON array of nations ranked by annual barrels of crude oil displaced. |

---

## 4. Running the Web Application on Windows

### Start Development Server
From the project root directory:
```powershell
python app.py
```

Expected terminal output:
```
[*] Starting VoltScope Web Server on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

### Open in Web Browser
Open your browser and navigate to:
- `http://127.0.0.1:5000/` — Executive Summary & Top Findings
- `http://127.0.0.1:5000/dashboard` — Interactive Dashboard / Tableau Embed
- `http://127.0.0.1:5000/story` — 4-Scene Narrative Story
- `http://127.0.0.1:5000/data` — Data Catalog & Provenance
- `http://127.0.0.1:5000/about` — Methodology & Stakeholders
