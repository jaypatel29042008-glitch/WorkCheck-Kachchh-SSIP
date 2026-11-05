"""
================================================================================
TEST SUITE: FASTAPI ENDPOINTS & FULL INTEGRATION (PS000109)
================================================================================
Verifies all REST API endpoints:
- Telemetry ingestion
- Worker profile & symptom reporting
- Worksite live watch & compliance update
- Mobile medical van queue & ABHA publishing
- District summaries & statutory exports
================================================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_workers():
    response = client.get("/api/workers?limit=10")
    assert response.status_code == 200
    workers = response.json()
    assert isinstance(workers, list)
    assert len(workers) > 0
    w = workers[0]
    assert "worker_id" in w
    assert "masked_eshram_uan" in w
    assert "abha_address" in w


def test_get_worker_profile():
    # First get a worker
    res = client.get("/api/workers?limit=1")
    workers = res.json()
    worker_id = workers[0]["worker_id"]

    response = client.get(f"/api/workers/{worker_id}")
    assert response.status_code == 200
    data = response.json()
    assert "worker" in data
    assert "pass_status" in data
    assert "statutory_rules" in data
    assert data["worker"]["worker_id"] == worker_id


def test_worker_symptom_logging():
    res = client.get("/api/workers?limit=1")
    workers = res.json()
    worker_id = workers[0]["worker_id"]

    payload = {
        "worker_id": worker_id,
        "dark_urine": True,
        "dizziness_or_fainting": True,
        "extreme_thirst": True,
        "persistent_cough": False,
        "eye_burning_salt_glare": True
    }
    response = client.post(f"/api/workers/{worker_id}/symptoms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SYMPTOMS_LOGGED"
    assert "symptom_id" in data


def test_list_sites():
    response = client.get("/api/sites")
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    assert len(sites) > 0
    s = sites[0]
    assert "site_id" in s
    assert "current_lamp_color" in s


def test_get_site_details():
    res = client.get("/api/sites")
    sites = res.json()
    site_id = sites[0]["site_id"]

    response = client.get(f"/api/sites/{site_id}")
    assert response.status_code == 200
    data = response.json()
    assert "site" in data
    assert "iso_7243_status" in data
    assert data["site"]["site_id"] == site_id


def test_telemetry_ingestion():
    res = client.get("/api/sites")
    sites = res.json()
    site_id = sites[0]["site_id"]

    payload = {
        "site_id": site_id,
        "device_id": "ESP32-TEST-NODE",
        "ambient_temp_c": 40.5,
        "relative_humidity_pct": 65.0,
        "pm2_5_ug_m3": 75.0,
        "uv_index": 9.0
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "TELEMETRY_RECORDED"
    assert "evaluation" in data
    assert "calculated_wbgt_c" in data["evaluation"]
    assert "lamp_color" in data["evaluation"]


def test_van_queue():
    response = client.get("/api/van/queue")
    assert response.status_code == 200
    queue = response.json()
    assert isinstance(queue, list)
    if len(queue) > 0:
        w = queue[0]
        assert "clinical_route" in w
        assert "route_label" in w
        assert "priority_score" in w


def test_van_publish_abha():
    # Fetch a worker from the van queue
    res = client.get("/api/van/queue")
    queue = res.json()
    assert len(queue) > 0
    target = queue[0]

    payload = {
        "case_id": target["case_id"],
        "worker_id": target["worker_id"],
        "doctor_registration_no": "GMC-KUTCH-MD-4081",
        "spirometry_fev1_liters": 2.90,
        "spirometry_fvc_liters": 3.70,
        "serum_creatinine_mg_dl": 1.02,
        "urine_specific_gravity": 1.016,
        "chest_xray_ilo_category": "0/0",
        "clinical_notes": "Periodic occupational examination completed with normal findings.",
        "bocw_assistance_claimed": True
    }
    response = client.post("/api/van/publish-abha", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESSFULLY_PUBLISHED_TO_ABHA"
    assert "abdm_confirmation" in data
    assert "fhir_bundle_summary" in data
    assert "sms_dispatch" in data
    assert data["abdm_confirmation"]["status"] == "PUBLISHED_TO_ABHA_LOCKER"


def test_district_summary():
    response = client.get("/api/district/summary")
    assert response.status_code == 200
    summary = response.json()
    assert isinstance(summary, list)


def test_statutory_exports():
    res_bocw = client.get("/api/district/export/bocw")
    assert res_bocw.status_code == 200
    assert "text/csv" in res_bocw.headers["content-type"]

    res_npcchh = client.get("/api/district/export/npcchh")
    assert res_npcchh.status_code == 200
    assert "application/json" in res_npcchh.headers["content-type"]


def test_cool_shift_stats():
    response = client.get("/api/cool-shift/stats")
    assert response.status_code == 200
    data = response.json()
    assert "sites_comparison" in data
    assert len(data["sites_comparison"]) == 5
