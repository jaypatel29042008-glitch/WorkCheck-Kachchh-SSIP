"""
================================================================================
FASTAPI API TEST RUNNER (UNITTEST)
================================================================================
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestWorkCheckAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_and_index(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("WorkCheck Kachchh", res.text)
        self.assertIn("PS000109", res.text)

    def test_02_list_workers(self):
        res = self.client.get("/api/workers?limit=10")
        self.assertEqual(res.status_code, 200)
        workers = res.json()
        self.assertIsInstance(workers, list)
        self.assertGreater(len(workers), 0)
        w = workers[0]
        self.assertIn("worker_id", w)
        self.assertIn("masked_eshram_uan", w)
        self.assertIn("abha_address", w)

    def test_03_get_worker_profile(self):
        res = self.client.get("/api/workers?limit=1")
        workers = res.json()
        worker_id = workers[0]["worker_id"]

        res2 = self.client.get(f"/api/workers/{worker_id}")
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertIn("worker", data)
        self.assertIn("pass_status", data)
        self.assertIn("statutory_rules", data)
        self.assertEqual(data["worker"]["worker_id"], worker_id)

    def test_04_worker_symptom_logging(self):
        res = self.client.get("/api/workers?limit=1")
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
        res2 = self.client.post(f"/api/workers/{worker_id}/symptoms", json=payload)
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertEqual(data["status"], "SYMPTOMS_LOGGED")
        self.assertIn("symptom_id", data)

    def test_05_list_sites(self):
        res = self.client.get("/api/sites")
        self.assertEqual(res.status_code, 200)
        sites = res.json()
        self.assertIsInstance(sites, list)
        self.assertGreater(len(sites), 0)
        s = sites[0]
        self.assertIn("site_id", s)
        self.assertIn("current_lamp_color", s)

    def test_06_get_site_details(self):
        res = self.client.get("/api/sites")
        sites = res.json()
        site_id = sites[0]["site_id"]

        res2 = self.client.get(f"/api/sites/{site_id}")
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertIn("site", data)
        self.assertIn("iso_7243_status", data)
        self.assertEqual(data["site"]["site_id"], site_id)

    def test_07_telemetry_ingestion(self):
        res = self.client.get("/api/sites")
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
        res2 = self.client.post("/api/telemetry", json=payload)
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertEqual(data["status"], "TELEMETRY_RECORDED")
        self.assertIn("evaluation", data)
        self.assertIn("calculated_wbgt_c", data["evaluation"])
        self.assertIn("lamp_color", data["evaluation"])

    def test_08_van_queue(self):
        res = self.client.get("/api/van/queue")
        self.assertEqual(res.status_code, 200)
        queue = res.json()
        self.assertIsInstance(queue, list)
        self.assertGreater(len(queue), 0)
        w = queue[0]
        self.assertIn("clinical_route", w)
        self.assertIn("route_label", w)
        self.assertIn("priority_score", w)

    def test_09_van_publish_abha(self):
        res = self.client.get("/api/van/queue")
        queue = res.json()
        self.assertGreater(len(queue), 0)
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
        res2 = self.client.post("/api/van/publish-abha", json=payload)
        self.assertEqual(res2.status_code, 200)
        data = res2.json()
        self.assertEqual(data["status"], "SUCCESSFULLY_PUBLISHED_TO_ABHA")
        self.assertIn("abdm_confirmation", data)
        self.assertIn("fhir_bundle_summary", data)
        self.assertIn("sms_dispatch", data)
        self.assertEqual(data["abdm_confirmation"]["status"], "PUBLISHED_TO_ABHA_LOCKER")

    def test_10_district_summary(self):
        res = self.client.get("/api/district/summary")
        self.assertEqual(res.status_code, 200)
        summary = res.json()
        self.assertIsInstance(summary, list)

    def test_11_statutory_exports(self):
        res_bocw = self.client.get("/api/district/export/bocw")
        self.assertEqual(res_bocw.status_code, 200)
        self.assertIn("text/csv", res_bocw.headers["content-type"])

        res_npcchh = self.client.get("/api/district/export/npcchh")
        self.assertEqual(res_npcchh.status_code, 200)
        self.assertIn("application/json", res_npcchh.headers["content-type"])

    def test_12_cool_shift_stats(self):
        res = self.client.get("/api/cool-shift/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sites_comparison", data)
        self.assertEqual(len(data["sites_comparison"]), 5)


if __name__ == "__main__":
    unittest.main()
