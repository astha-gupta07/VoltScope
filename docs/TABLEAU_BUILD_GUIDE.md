# VoltScope — Complete Tableau Build & Design Manual
## Step-by-Step Instructions for Visualizations, Calculated Fields, Dashboard & Story

This manual provides instructions for opening **Tableau Desktop** or **Tableau Public**, connecting to the prepared data extracts in `VoltScope/data/exports/tableau/`, constructing the 6 core analytical worksheets, creating the 5 calculated fields, assembling the Executive Dashboard, building the 4-Scene Tableau Story, and publishing to Tableau Public.

---

## 1. Connecting Data in Tableau

1. **Open Tableau**: Launch Tableau Desktop or Tableau Public.
2. **Connect to Primary Sales Extract**:
   - In the left pane under **To a File**, select **Text file**.
   - Browse to `VoltScope/data/exports/tableau/tableau_ev_market_sales.csv`.
   - Verify data types:
     - `Month Date`: Recognized as **Date** (calendar icon).
     - `Country`: Recognized as **Geographic Role** -> **Country/Region** (globe icon).
     - `Registrations`: Recognized as **Measure** (`#`).
3. **Add Secondary Data Sources** (Keep Separate, Do NOT Join!):
   - In the top menu, click **Data** -> **New Data Source** -> **Text file**.
   - Select `tableau_vehicle_specifications.csv`.
   - Again, click **Data** -> **New Data Source** -> **Text file**.
   - Select `tableau_ev_fleet_sustainability.csv`.
   - *Data Integrity Reminder*: Maintaining these as three independent data sources prevents accidental row inflation and duplicate counts.

---

## 2. Creating the 5 Tableau Calculated Fields

In Tableau, right-click anywhere in the **Data Pane** on the left and select **Create Calculated Field...**:

### Calculated Field 1: `[YoY EV Sales Growth %]`
- **Data Source**: `tableau_ev_market_sales.csv`
- **Purpose**: Computes the percentage change in registrations compared to the same month in the previous year.
- **Formula**:
```tableau
(ZN(SUM([Registrations])) - LOOKUP(ZN(SUM([Registrations])), -12)) 
/ ABS(LOOKUP(ZN(SUM([Registrations])), -12))
```
- **Formatting**: Right-click the field -> **Default Properties** -> **Number Format** -> **Percentage** (1 decimal place).

### Calculated Field 2: `[EV Market Penetration %]`
- **Data Source**: `tableau_ev_market_sales.csv`
- **Purpose**: Computes average electric vehicle penetration relative to total passenger car market.
- **Formula**:
```tableau
IF [Is Aggregate Drivetrain] = True AND [Drivetrain] = 'Electric vehicle (BEV+PHEV)' 
THEN [Market Share %] 
END
```
- **Formatting**: Percentage (1 decimal place).

### Calculated Field 3: `[Driving Efficiency (km/kWh)]`
- **Data Source**: `tableau_vehicle_specifications.csv`
- **Purpose**: Measures specific range utility per kilowatt-hour of battery pack.
- **Formula**:
```tableau
IF ZN([Battery Capacity (kWh)]) > 0 
THEN ROUND([WLTP Range (km)] / [Battery Capacity (kWh)], 2)
ELSE NULL 
END
```
- **Formatting**: Number (Standard, 2 decimals).

### Calculated Field 4: `[Range Segment Group]`
- **Data Source**: `tableau_vehicle_specifications.csv`
- **Purpose**: Categorizes models into practical driving range utility tiers.
- **Formula**:
```tableau
IF [WLTP Range (km)] < 300 THEN '1. Urban (< 300 km)'
ELSEIF [WLTP Range (km)] <= 499 THEN '2. Standard (300 - 499 km)'
ELSEIF [WLTP Range (km)] <= 649 THEN '3. Long Range (500 - 649 km)'
ELSE '4. Ultra Range (650+ km)'
END
```
- **Formatting**: Dimension / Text.

### Calculated Field 5: `[Fast Charge Capability Flag]`
- **Data Source**: `tableau_vehicle_specifications.csv`
- **Purpose**: Identifies vehicles capable of highway rapid charging (>100 kW).
- **Formula**:
```tableau
IF [DC Fast Charge Power (kW)] >= 150 THEN 'Ultra-Fast (150+ kW)'
ELSEIF [DC Fast Charge Power (kW)] >= 50 THEN 'Fast (50 - 149 kW)'
ELSE 'Standard / AC Only (< 50 kW)'
END
```
- **Formatting**: Dimension / Text.

---

## 3. Building the 6 Core Worksheets

### Sheet 1: Global EV Sales Trajectory Over Time
- **Chart Type**: Dual-Axis Line Chart
- **Data Source**: `tableau_ev_market_sales.csv`
- **Filters**:
  - Drag `Drivetrain` to **Filters** -> Select `'Electric vehicle (BEV+PHEV)'`.
  - Drag `Month Date` to **Filters** -> Range of dates from `2015-01-01` to latest.
- **Columns**: `Month Date` (Right-click and select **Continuous Month**: `Month YYYY`).
- **Rows**:
  1. `SUM(Registrations)`
  2. `SUM(Rolling 12M Registrations)` (Divide by 12 in shelf or create calculated field).
- **Marks Card**:
  - `SUM(Registrations)`: Mark Type = **Line**, Color = Deep Teal (`#0d9488`), Size = Medium.
  - `Rolling 12M`: Mark Type = **Line**, Color = Navy Blue (`#0284c7`), Style = Dashed.
- **Format**: Right-click right axis -> **Dual Axis** -> Right-click axis -> **Synchronize Axis**. Set Y-axis title: "Monthly New Registrations".

### Sheet 2: Top Sovereign EV Markets (2025 Calendar Sales)
- **Chart Type**: Horizontal Ranked Bar Chart
- **Data Source**: `tableau_ev_market_sales.csv`
- **Filters**:
  - Drag `Year` to **Filters** -> Select `2025`.
  - Drag `Is Aggregate Drivetrain` to **Filters** -> Select `True`.
  - Drag `Drivetrain` to **Filters** -> Select `'Electric vehicle (BEV+PHEV)'`.
- **Columns**: `SUM(Registrations)`
- **Rows**: `Country`
- **Sort**: Click the sort icon on `Country` -> Sort descending by `SUM(Registrations)`.
- **Marks**:
  - Color: Drag `Continent` to **Color**.
  - Label: Click **Label** -> Check **Show mark labels**.
  - Tooltip: Include `Country`, `2025 Registrations`, and `Market Share %`.

### Sheet 3: Drivetrain Mix Transformation Over Time
- **Chart Type**: 100% Stacked Bar / Area Chart
- **Data Source**: `tableau_drivetrain_mix_annual.csv`
- **Columns**: `Year` (Discrete)
- **Rows**: `SUM(Total Registrations)`
- **Marks**:
  - Mark Type: **Bar** (or **Area**).
  - Drag `Drivetrain` to **Color**:
    - `Battery electric`: Teal (`#0d9488`)
    - `Plug-in hybrid`: Light Cyan (`#38bdf8`)
    - `Hybrid`: Amber (`#f59e0b`)
    - `Petrol`: Slate Grey (`#64748b`)
    - `Diesel`: Dark Slate (`#334155`)
  - Quick Table Calculation on `SUM(Total Registrations)`:
    - Right-click measure -> **Quick Table Calculation** -> **Percent of Total**.
    - Compute Using: **Table (Down)** or **Drivetrain**.

### Sheet 4: Battery Capacity vs Driving Range Scatter Plot
- **Chart Type**: Scatter Plot with Linear Trendline
- **Data Source**: `tableau_vehicle_specifications.csv`
- **Filters**:
  - Drag `Battery Capacity (kWh)` to **Filters** -> At least 10.
  - Drag `WLTP Range (km)` to **Filters** -> At least 50.
- **Columns**: `Battery Capacity (kWh)` (Measure: Continuous)
- **Rows**: `WLTP Range (km)` (Measure: Continuous)
- **Detail**: Drag `Model Name` and `Brand` to **Detail** on Marks Card.
- **Color**: Drag `Vehicle Category` to **Color**.
- **Trendline**: In the **Analytics** pane on the left, drag **Trend Line** onto the chart -> Select **Linear**.

### Sheet 5: Driving Range by Vehicle Category
- **Chart Type**: Box-and-Whisker / Category Bar Comparison
- **Data Source**: `tableau_vehicle_specifications.csv`
- **Columns**: `Vehicle Category`
- **Rows**: `AVG(WLTP Range (km))` and `AVG(DC Fast Charge Power (kW))`
- **Marks**:
  - Mark Type = **Bar**, Color = Teal (`#0d9488`).
  - Add reference lines or Box Plot from the Analytics pane to visualize range variance.

### Sheet 6: National Petroleum Displaced & Sustainability Map
- **Chart Type**: Symbol Map or Choropleth Filled Map
- **Data Source**: `tableau_ev_fleet_sustainability.csv`
- **Detail**: Drag `Country` (Geographic Role) to **Detail**.
- **Size / Color**:
  - Drag `[Oil Displaced (Thousand Bbl/Yr)]` to **Color** (Palette: Green-Blue or Teal sequential).
  - Drag `[EV Fleet Vehicles]` to **Size**.
- **Tooltip**: Displays Country, EV Fleet Size, Oil Displaced (Thousand Bbl/Yr), and Economic Value ($M).

---

## 4. Designing the Executive Dashboard

1. **Create Dashboard**: Click the **New Dashboard** icon at the bottom of Tableau.
2. **Size**: Set Dashboard Size to **Fixed Size** -> **Desktop Browser (1366 x 768)** or **Automatic**.
3. **Visual Hierarchy & Layout**:
   - **Header Container (Horizontal, Top)**:
     - Title: **VoltScope — EV Market Performance & Intelligence**
     - Subtitle: Global Sales Trajectory, Powertrain Dynamics & Engineering Benchmarks
   - **KPI Summary Row**:
     - 4 Text / Card tiles showing: Total 2025 Sales (14M+), Active Fleet (40M+), Petroleum Displaced (1.4M+ bbl/yr), Mean Range (468 km).
   - **Main Analysis Area (2x2 Grid)**:
     - Top-Left: **Sheet 1: Global EV Sales Trajectory Over Time**
     - Top-Right: **Sheet 2: Top Sovereign EV Markets**
     - Bottom-Left: **Sheet 3: Drivetrain Transition Over Time**
     - Bottom-Right: **Sheet 4: Battery Capacity vs Driving Range Scatter**
   - **Interactive Filters (Top Right or Right Sidebar)**:
     - Year Filter (Single Value Dropdown)
     - Continent Filter (Multiple Values Dropdown)
     - Vehicle Category Filter
     - Apply to Worksheets -> **All Using Related Data Sources**.
4. **Device Layout**:
   - In the Dashboard pane, click **Device Preview** -> Add **Phone** layout.
   - Stack worksheets vertically for responsive mobile viewing.

---

## 5. Building the 4-Scene Tableau Story

1. **Create Story**: Click the **New Story** icon at the bottom.
2. **Story Size**: Set to **Automatic** or **1280 x 800**.
3. **Scene 1: The EV Market at a Glance**:
   - Story Point Title: *The EV Market at a Glance*
   - Drag **Sheet 1 (Sales Trajectory)** into the canvas.
   - Description Box: *"Global monthly electric vehicle registrations have surged past 1.5 million units. Pure BEVs represent over two-thirds of all new electric registrations, demonstrating resilient compounding growth."*
4. **Scene 2: Where Adoption Is Growing**:
   - Click **Blank** to create Scene 2.
   - Title: *Where Adoption Is Growing*
   - Drag **Sheet 2 (Top Markets)** and **Sheet 6 (Sustainability Map)**.
   - Description Box: *"Adoption is heavily concentrated in China, Western Europe, and the United States, while Nordic nations lead the world in relative market share (85%+)."*
5. **Scene 3: Vehicle Performance and Technology**:
   - Click **Blank** to create Scene 3.
   - Title: *Vehicle Performance and Technology*
   - Drag **Sheet 4 (Battery vs Range)** and **Sheet 5 (Category Benchmarks)**.
   - Description Box: *"Across 166 models, driving range scales at ~5.8 km/kWh. Aerodynamic sedans achieve peak range efficiency, while SUVs dominate consumer model offerings (53.6%)."*
6. **Scene 4: Strategic Insights & Recommendations**:
   - Click **Blank** to create Scene 4.
   - Title: *Strategic Insights & Recommendations*
   - Add summary visual cards and strategic takeaways tailored for Emily Johnson, David Chen, and Dr. Sarah Williams.

---

## 6. Publishing to Tableau Public & Configuring Flask

1. **Save to Tableau Public**:
   - In Tableau Desktop, click **Server** -> **Tableau Public** -> **Save to Tableau Public As...**.
   - Sign in with your free Tableau Public account.
   - Save the workbook as: `VoltScope_EV_Market_Analytics`.
2. **Copy Published Embed URLs**:
   - In your web browser, open your published Tableau Public dashboard and story.
   - Click the **Share** icon on the bottom toolbar.
   - Copy the **Link** (e.g., `https://public.tableau.com/views/VoltScope/ExecutiveDashboard`).
3. **Configure VoltScope `.env`**:
   - Open your project `.env` file and paste the URLs:
   ```env
   TABLEAU_DASHBOARD_URL="https://public.tableau.com/views/VoltScope/ExecutiveDashboard"
   TABLEAU_STORY_URL="https://public.tableau.com/views/VoltScope/EVStory"
   ```
4. **Verify in Flask**:
   - Refresh `http://127.0.0.1:5000/dashboard` and `http://127.0.0.1:5000/story`.
   - The official Tableau Embedding API v3 `<tableau-viz>` component will automatically render your live published views!
