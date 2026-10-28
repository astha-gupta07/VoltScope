/**
 * VoltScope — Executive BI Dashboard & Story Visualizations
 * Connects to local Flask REST endpoints and renders interactive Chart.js charts.
 */

let charts = {};
let cachedData = {};

document.addEventListener("DOMContentLoaded", () => {
    // Check if dashboard canvas exists
    if (document.getElementById("chartSalesTrend")) {
        initDashboard();
    }
    
    // Check if story canvas exists
    if (document.getElementById("storyChart1")) {
        initStory();
    }
});

// ==============================================================================
// Dashboard Initialization & Data Fetching
// ==============================================================================
async function initDashboard() {
    try {
        const [salesRes, mixRes, topRes, specsRes, sustRes] = await Promise.all([
            fetch("/api/sales-trend").then(r => r.json()),
            fetch("/api/drivetrain-mix").then(r => r.json()),
            fetch("/api/top-countries").then(r => r.json()),
            fetch("/api/specs-by-category").then(r => r.json()),
            fetch("/api/sustainability").then(r => r.json())
        ]);

        cachedData = {
            salesTrend: salesRes,
            drivetrainMix: mixRes,
            topCountries: topRes,
            specsByCategory: specsRes,
            sustainability: sustRes
        };

        renderChartSalesTrend(cachedData.salesTrend);
        renderChartTopCountries(cachedData.topCountries);
        renderChartDrivetrainMix(cachedData.drivetrainMix);
        renderChartBatteryVsRange();
        renderChartCategorySpecs(cachedData.specsByCategory);
        renderChartSustainability(cachedData.sustainability);

    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

// Chart 1: Sales Trajectory Over Time
function renderChartSalesTrend(data) {
    const ctx = document.getElementById("chartSalesTrend");
    if (!ctx) return;

    const labels = data.map(d => d.date);
    const registrations = data.map(d => d.registrations);
    const rolling12m = data.map(d => d.rolling_12m_registrations ? d.rolling_12m_registrations / 12 : null);

    if (charts.salesTrend) charts.salesTrend.destroy();

    charts.salesTrend = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Monthly Registrations",
                    data: registrations,
                    borderColor: "#0d9488",
                    backgroundColor: "rgba(13, 148, 136, 0.08)",
                    borderWidth: 2,
                    pointRadius: 1,
                    tension: 0.2,
                    fill: true
                },
                {
                    label: "12-Month Moving Avg",
                    data: rolling12m,
                    borderColor: "#0284c7",
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    tension: 0.2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${Math.round(ctx.raw).toLocaleString()} units`
                    }
                }
            },
            scales: {
                x: { ticks: { maxTicksLimit: 12, font: { size: 10 } }, grid: { display: false } },
                y: {
                    ticks: {
                        callback: val => val >= 1000000 ? (val / 1000000).toFixed(1) + "M" : val.toLocaleString(),
                        font: { size: 10 }
                    },
                    grid: { color: "#f1f5f9" }
                }
            }
        }
    });
}

// Chart 2: Top Sovereign EV Markets
function renderChartTopCountries(data) {
    const ctx = document.getElementById("chartTopCountries");
    if (!ctx) return;

    const sorted = [...data].slice(0, 10).reverse();
    const labels = sorted.map(d => d.country);
    const sales = sorted.map(d => d.annual_ev_sales);

    if (charts.topCountries) charts.topCountries.destroy();

    charts.topCountries = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "2025 EV Sales",
                data: sales,
                backgroundColor: "#0d9488",
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `2025 Registrations: ${Math.round(ctx.raw).toLocaleString()} units`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: val => val >= 1000000 ? (val / 1000000).toFixed(1) + "M" : val.toLocaleString(),
                        font: { size: 10 }
                    },
                    grid: { color: "#f1f5f9" }
                },
                y: { ticks: { font: { size: 10, weight: 600 } }, grid: { display: false } }
            }
        }
    });
}

// Chart 3: Drivetrain Mix Transformation
function renderChartDrivetrainMix(data) {
    const ctx = document.getElementById("chartDrivetrainMix");
    if (!ctx) return;

    // Group by year
    const years = [...new Set(data.map(d => d.year))].sort();
    const drivetrains = ["Battery electric", "Plug-in hybrid", "Hybrid", "Petrol", "Diesel"];
    const colors = {
        "Battery electric": "#0d9488",
        "Plug-in hybrid": "#38bdf8",
        "Hybrid": "#f59e0b",
        "Petrol": "#64748b",
        "Diesel": "#94a3b8"
    };

    const datasets = drivetrains.map(dt => {
        const values = years.map(yr => {
            const row = data.find(d => d.year === yr && d.drivetrain === dt);
            return row ? row.share_pct : 0;
        });
        return {
            label: dt,
            data: values,
            backgroundColor: colors[dt] || "#cbd5e1"
        };
    });

    if (charts.drivetrainMix) charts.drivetrainMix.destroy();

    charts.drivetrainMix = new Chart(ctx, {
        type: "bar",
        data: { labels: years, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top", labels: { boxWidth: 10, font: { size: 10 } } },
                tooltip: {
                    callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw}% avg share` }
                }
            },
            scales: {
                x: { stacked: true, grid: { display: false }, ticks: { font: { size: 10 } } },
                y: {
                    stacked: true,
                    max: 100,
                    ticks: { callback: val => `${val}%`, font: { size: 10 } },
                    grid: { color: "#f1f5f9" }
                }
            }
        }
    });
}

// Chart 4: Battery vs Driving Range Scatter
async function renderChartBatteryVsRange() {
    const ctx = document.getElementById("chartBatteryVsRange");
    if (!ctx) return;

    // Direct sample points for scatter
    const sampleModels = [
        { brand: "Tesla", model: "Model 3 LR", kwh: 75, range: 629, cat: "Sedan" },
        { brand: "Tesla", model: "Model Y", kwh: 75, range: 533, cat: "SUV" },
        { brand: "Volkswagen", model: "ID.4 Pro", kwh: 77, range: 530, cat: "SUV" },
        { brand: "Hyundai", model: "Ioniq 5 LR", kwh: 84, range: 570, cat: "SUV" },
        { brand: "BMW", model: "i4 eDrive40", kwh: 81, range: 590, cat: "Sedan" },
        { brand: "Volvo", model: "EX30 ER", kwh: 64, range: 476, cat: "SUV" },
        { brand: "Renault", model: "Megane E-Tech", kwh: 60, range: 450, cat: "Hatchback" },
        { brand: "Peugeot", model: "e-208", kwh: 51, range: 400, cat: "Hatchback" },
        { brand: "Porsche", model: "Taycan Plus", kwh: 97, range: 678, cat: "Sedan" },
        { brand: "Lucid", model: "Air Grand Touring", kwh: 118, range: 883, cat: "Sedan" },
        { brand: "Kia", model: "EV9 AWD", kwh: 99.8, range: 505, cat: "SUV" },
        { brand: "Audi", model: "Q4 e-tron", kwh: 77, range: 534, cat: "SUV" },
        { brand: "MG", model: "MG4 Standard", kwh: 51, range: 350, cat: "Hatchback" },
        { brand: "Polestar", model: "Polestar 2 LR", kwh: 79, range: 655, cat: "Sedan" },
        { brand: "Skoda", model: "Enyaq iV 80", kwh: 77, range: 544, cat: "SUV" }
    ];

    const scatterData = sampleModels.map(m => ({
        x: m.kwh,
        y: m.range,
        title: `${m.brand} ${m.model} (${m.cat})`
    }));

    if (charts.batteryVsRange) charts.batteryVsRange.destroy();

    charts.batteryVsRange = new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: [{
                label: "EV Models (Battery vs Range)",
                data: scatterData,
                backgroundColor: "#0d9488",
                borderColor: "#0f766e",
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const p = ctx.raw;
                            return `${p.title}: ${p.x} kWh -> ${p.y} km (${(p.y/p.x).toFixed(2)} km/kWh)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Battery Pack Capacity (kWh)", font: { size: 11, weight: 600 } },
                    grid: { color: "#f1f5f9" }
                },
                y: {
                    title: { display: true, text: "WLTP Certified Range (km)", font: { size: 11, weight: 600 } },
                    grid: { color: "#f1f5f9" }
                }
            }
        }
    });
}

// Chart 5: Category Benchmarks
function renderChartCategorySpecs(data) {
    const ctx = document.getElementById("chartCategorySpecs");
    if (!ctx) return;

    const filtered = data.filter(d => d.body_category !== "Unknown" && d.total_models >= 2);
    const labels = filtered.map(d => d.body_category);
    const avgRanges = filtered.map(d => d.avg_range_km);
    const avgFastCharge = filtered.map(d => d.avg_fast_charge_dc_kw);

    if (charts.categorySpecs) charts.categorySpecs.destroy();

    charts.categorySpecs = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Avg Range (km)",
                    data: avgRanges,
                    backgroundColor: "#0d9488",
                    borderRadius: 4,
                    yAxisID: "y"
                },
                {
                    label: "Avg DC Charge (kW)",
                    data: avgFastCharge,
                    backgroundColor: "#0284c7",
                    borderRadius: 4,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top", labels: { boxWidth: 10, font: { size: 10 } } }
            },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 10 } } },
                y: {
                    type: "linear",
                    position: "left",
                    title: { display: true, text: "Range (km)", font: { size: 10 } },
                    grid: { color: "#f1f5f9" }
                },
                y1: {
                    type: "linear",
                    position: "right",
                    title: { display: true, text: "DC Power (kW)", font: { size: 10 } },
                    grid: { display: false }
                }
            }
        }
    });
}

// Chart 6: Sustainability Barrels Displaced
function renderChartSustainability(data) {
    const ctx = document.getElementById("chartSustainability");
    if (!ctx) return;

    const sorted = [...data].slice(0, 8).reverse();
    const labels = sorted.map(d => d.country);
    const oil = sorted.map(d => d.oil_displaced_thousand_bbl);

    if (charts.sustainability) charts.sustainability.destroy();

    charts.sustainability = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Displaced Oil (Thousand Bbl/Yr)",
                data: oil,
                backgroundColor: "#0284c7",
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `${Math.round(ctx.raw).toLocaleString()} thousand barrels displaced/yr`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        callback: val => val >= 1000 ? (val / 1000).toFixed(1) + "M" : val.toLocaleString(),
                        font: { size: 10 }
                    },
                    grid: { color: "#f1f5f9" }
                },
                y: { ticks: { font: { size: 10, weight: 600 } }, grid: { display: false } }
            }
        }
    });
}

// Filter handlers
function applyFilters() {
    const yearVal = document.getElementById("filterYear").value;
    const catVal = document.getElementById("filterCategory").value;
    const feedback = document.getElementById("filterFeedback");
    
    feedback.textContent = `Active filter: Year=${yearVal}, Category=${catVal}`;
    feedback.style.color = "#0d9488";
}

function resetFilters() {
    document.getElementById("filterYear").value = "2025";
    document.getElementById("filterCategory").value = "all";
    document.getElementById("filterMetric").value = "sales";
    const feedback = document.getElementById("filterFeedback");
    feedback.textContent = "Showing verified SQLite records (Filters reset)";
    feedback.style.color = "#64748b";
}


// ==============================================================================
// Story Walkthrough Scene Switching & Visuals
// ==============================================================================
function switchStoryScene(sceneNum) {
    // Hide all scenes
    for (let i = 1; i <= 4; i++) {
        const sc = document.getElementById(`scene-${i}`);
        if (sc) sc.style.display = i === sceneNum ? "block" : "none";
    }

    // Update active tab buttons
    const tabs = document.querySelectorAll(".story-tab");
    tabs.forEach((tab, idx) => {
        if (idx === sceneNum - 1) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    // Lazy load chart for active scene if needed
    renderStorySceneVisual(sceneNum);
}

function initStory() {
    renderStorySceneVisual(1);
}

function renderStorySceneVisual(sceneNum) {
    if (sceneNum === 1) {
        const ctx = document.getElementById("storyChart1");
        if (ctx && !charts.story1) {
            fetch("/api/sales-trend").then(r => r.json()).then(data => {
                const labels = data.slice(-48).map(d => d.date);
                const regs = data.slice(-48).map(d => d.registrations);
                charts.story1 = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Global Monthly EV Registrations",
                            data: regs,
                            borderColor: "#0d9488",
                            backgroundColor: "rgba(13, 148, 136, 0.1)",
                            fill: true,
                            tension: 0.2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { maxTicksLimit: 8, font: { size: 10 } } },
                            y: { ticks: { callback: v => (v/1000000).toFixed(1) + "M" } }
                        }
                    }
                });
            });
        }
    } else if (sceneNum === 2) {
        const ctx = document.getElementById("storyChart2");
        if (ctx && !charts.story2) {
            fetch("/api/top-countries").then(r => r.json()).then(data => {
                const top7 = data.slice(0, 7);
                charts.story2 = new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: top7.map(d => d.country),
                        datasets: [{
                            label: "2025 EV Sales",
                            data: top7.map(d => d.annual_ev_sales),
                            backgroundColor: "#0284c7",
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { ticks: { callback: v => v >= 1000000 ? (v/1000000).toFixed(1) + "M" : v.toLocaleString() } }
                        }
                    }
                });
            });
        }
    } else if (sceneNum === 3) {
        const ctx = document.getElementById("storyChart3");
        if (ctx && !charts.story3) {
            fetch("/api/specs-by-category").then(r => r.json()).then(data => {
                charts.story3 = new Chart(ctx, {
                    type: "radar",
                    data: {
                        labels: data.map(d => d.body_category),
                        datasets: [{
                            label: "Average WLTP Range (km)",
                            data: data.map(d => d.avg_range_km),
                            borderColor: "#0d9488",
                            backgroundColor: "rgba(13, 148, 136, 0.2)"
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: "top" } }
                    }
                });
            });
        }
    } else if (sceneNum === 4) {
        const ctx = document.getElementById("storyChart4");
        if (ctx && !charts.story4) {
            fetch("/api/sustainability").then(r => r.json()).then(data => {
                const top6 = data.slice(0, 6);
                charts.story4 = new Chart(ctx, {
                    type: "doughnut",
                    data: {
                        labels: top6.map(d => d.country),
                        datasets: [{
                            data: top6.map(d => d.oil_displaced_thousand_bbl),
                            backgroundColor: ["#0d9488", "#0284c7", "#38bdf8", "#f59e0b", "#64748b", "#94a3b8"]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: "right", labels: { boxWidth: 10, font: { size: 10 } } } }
                    }
                });
            });
        }
    }
}
