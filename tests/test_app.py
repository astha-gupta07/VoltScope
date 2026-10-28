"""
Unit Tests: Flask Web Application Routes & APIs
Verifies HTTP 200 responses, template rendering, JSON API structure, and embedding fallback.
"""

import sys
import pytest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test Home / Executive Overview returns 200 and renders KPI metrics."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"VoltScope" in res.data
    assert b"Executive Market Intelligence" in res.data
    assert b"Top Sovereign EV Markets" in res.data


def test_dashboard_route(client):
    """Test Dashboard route returns 200 and includes fallback or Tableau elements."""
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"chartSalesTrend" in res.data or b"tableau-viz" in res.data


def test_story_route(client):
    """Test Story route returns 200 and includes scene narrative containers."""
    res = client.get("/story")
    assert res.status_code == 200
    assert b"Scene 1 of 4" in res.data or b"tableau-viz" in res.data


def test_data_catalog_route(client):
    """Test Data catalog route returns 200 and displays dataset sources."""
    res = client.get("/data")
    assert res.status_code == 200
    assert b"Ember Monthly EV Sales Data" in res.data
    assert b"CC BY 4.0" in res.data


def test_about_route(client):
    """Test About route returns 200 and lists all 3 stakeholders."""
    res = client.get("/about")
    assert res.status_code == 200
    assert b"Emily Johnson" in res.data
    assert b"David Chen" in res.data
    assert b"Dr. Sarah Williams" in res.data


def test_api_endpoints_return_json(client):
    """Verify all 5 REST API endpoints return HTTP 200 and valid JSON lists."""
    endpoints = [
        "/api/sales-trend",
        "/api/drivetrain-mix",
        "/api/specs-by-category",
        "/api/top-countries",
        "/api/sustainability"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} returned status {res.status_code}"
        assert res.is_json, f"Endpoint {ep} did not return JSON"
        data = res.get_json()
        assert isinstance(data, list), f"Endpoint {ep} expected list, got {type(data)}"
        assert len(data) > 0, f"Endpoint {ep} returned an empty list"
