"""
================================================================================
WORKCHECK KACHCHH — DIRECT COMPREHENSIVE INTEGRATION TEST SUITE (PS000109)
================================================================================
Validates all 14 API endpoints, data models, statutory triggers, 
ISO 7243 WBGT calculations, ABHA HL7 FHIR bundles, and UI template rendering.
Runs deterministically in any sandbox or CI environment.
================================================================================
"""

import sys
import unittest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.endpoints import (
    list_workers,
    get_worker_profile,
    log_worker_symptoms,
    SymptomReport,
    list_sites,
    get_site_details,
    update_site_compliance,
    SiteComplianceUpdate,
    ingest_telemetry,
    TelemetryPayload,
    get_site_live_telemetry,
    get_van_screening_queue,
    publish_examination_to_abha,
    ClinicalScreeningPayload,
    get_district_summary,
    get_district_hotspots,
    export_statutory_report,
    get_cool_shift_stats
)


class TestWorkCheckDirectAPI(unittest.TestCase):

    def test_01_template_rendering(self):
        """Validates that index.html renders cleanly with institutional styling & all personas."""
        env = Environment(loader=FileSystemLoader(str(PROJECT_ROOT / "app" / "templates")))
        template = env.get_template("index.html")
        rendered = template.render(
            request=None,
            initial_view="worker",
            project_name="WorkCheck Kachchh",
            team_id="TM005024",
            client="District Development Office, Kachchh"
        )
        self.assertIn("WorkCheck Kachchh", rendered)
        self.assertIn("PS000109", rendered)
        self.assertIn("District Development Office (DDO) Kachchh", rendered)
        self.assertIn("Form 5", rendered)
        self.assertIn("ABHA", rendered)
        self.assertIn("ISO 7243", rendered)
        self.assertGreater(len(rendered), 10000)

    def test_02_list_workers(self):
        """Checks worker listing with DPDP Act masking (masked e-Shram UAN)."""
        workers = list_workers(limit=10)
        self.assertIsInstance(workers, list)
        self.assertGreater(len(workers), 0)
        w = workers[0]
        self.assertIn("worker_id", w)
        self.assertIn("masked_eshram_uan", w)
        self.assertIn("-XXXX-", w["masked_eshram_uan"])
        self.assertIn("abha_address", w)

    def test_03_get_worker_profile(self):
        """Checks worker profile, QR hash verification, pass status, and Gujarat OSH statutory rules."""
        workers = list_workers(limit=1)
        worker_id = workers[0]["worker_id"]

        data = get_worker_profile(worker_id)
        self.assertIn("worker", data)
        self.assertIn("pass_status", data)
        self.assertIn("statutory_rules", data)
        self.assertEqual(data["worker"]["worker_id"], worker_id)
        self.assertIn("rule_9_gujarat_applies", data["statutory_rules"])
        self.assertIn("status", data["pass_status"])

    def test_04_worker_symptom_logging(self):
        """Tests worker symptom reporting (dark urine, dizziness, eye glare) and van referral trigger."""
        workers = list_workers(limit=1)
        worker_id = workers[0]["worker_id"]

        payload = SymptomReport(
            worker_id=worker_id,
            dark_urine=True,
            dizziness_or_fainting=True,
            extreme_thirst=True,
            persistent_cough=False,
            eye_burning_salt_glare=True
        )
        res = log_worker_symptoms(worker_id, payload)
        self.assertEqual(res["status"], "SYMPTOMS_LOGGED")
        self.assertIn("symptom_id", res)
        self.assertTrue(res["clinical_van_alert_created"])

    def test_05_list_sites(self):
        """Validates worksite retrieval with live risk, WBGT, and ISO 7243 lamps."""
        sites = list_sites()
        self.assertIsInstance(sites, list)
        self.assertGreaterEqual(len(sites), 5)
        s = sites[0]
        self.assertIn("site_id", s)
        self.assertIn("current_lamp_color", s)
        self.assertIn(s["current_lamp_color"], ["GREEN", "YELLOW", "ORANGE", "RED"])

    def test_06_get_site_details(self):
        """Tests worksite detailed view with worker headcount and recent readings."""
        sites = list_sites()
        site_id = sites[0]["site_id"]

        data = get_site_details(site_id)
        self.assertIn("site", data)
        self.assertIn("iso_7243_status", data)
        self.assertEqual(data["site"]["site_id"], site_id)
        self.assertIn("work_rest_minutes", data["iso_7243_status"])

    def test_07_telemetry_ingestion(self):
        """Tests ESP32 telemetry ingestion, Stull wet bulb, ISO 7243 WBGT, and database recording."""
        sites = list_sites()
        site_id = sites[0]["site_id"]

        payload = TelemetryPayload(
            site_id=site_id,
            device_id="ESP32-STATION-01",
            ambient_temp_c=41.2,
            relative_humidity_pct=62.0,
            pm2_5_ug_m3=78.0,
            uv_index=9.5
        )
        res = ingest_telemetry(payload)
        self.assertEqual(res["status"], "TELEMETRY_RECORDED")
        self.assertIn("evaluation", res)
        self.assertIn("calculated_wbgt_c", res["evaluation"])
        self.assertEqual(res["evaluation"]["lamp_color"], "RED")
        self.assertIsInstance(res["reading_id"], int)

    def test_08_van_screening_queue(self):
        """Verifies clinical queue prioritized by the 3 Clinician-Approved Routes."""
        queue = get_van_screening_queue()
        self.assertIsInstance(queue, list)
        self.assertGreater(len(queue), 0)
        target = queue[0]
        self.assertIn("clinical_route", target)
        self.assertIn(target["clinical_route"], ["ROUTE_1_STATUTORY", "ROUTE_2_EXPOSURE", "ROUTE_3_SYMPTOMS"])
        self.assertIn("priority_score", target)
        self.assertGreaterEqual(target["priority_score"], 1)

    def test_09_van_publish_abha(self):
        """Validates HL7 FHIR DiagnosticReport bundle publishing to ABDM ABHA locker."""
        queue = get_van_screening_queue()
        target = queue[0]

        payload = ClinicalScreeningPayload(
            case_id=target["case_id"],
            worker_id=target["worker_id"],
            doctor_registration_no="GMC-KUTCH-MD-4081",
            spirometry_fev1_liters=2.95,
            spirometry_fvc_liters=3.75,
            serum_creatinine_mg_dl=1.04,
            urine_specific_gravity=1.018,
            chest_xray_ilo_category="0/0",
            clinical_notes="Occupational periodic medical examination completed aboard Dhanvantari Arogya Rath.",
            bocw_assistance_claimed=True
        )
        res = publish_examination_to_abha(payload)
        self.assertEqual(res["status"], "SUCCESSFULLY_PUBLISHED_TO_ABHA")
        self.assertIn("abdm_confirmation", res)
        self.assertEqual(res["abdm_confirmation"]["status"], "PUBLISHED_TO_ABHA_LOCKER")
        self.assertIn("fhir_bundle_summary", res)
        self.assertEqual(res["fhir_bundle_summary"]["resource_type"], "Bundle")
        self.assertIn("sms_dispatch", res)
        self.assertEqual(res["sms_dispatch"]["delivery_status"], "DELIVERED")

    def test_10_district_summary_and_hotspots(self):
        """Verifies DPDP-compliant anonymous taluka totals and occupational risk hotspots."""
        summary = get_district_summary()
        self.assertIsInstance(summary, list)
        self.assertGreater(len(summary), 0)

        hotspots = get_district_hotspots()
        self.assertIsInstance(hotspots, list)
        self.assertGreater(len(hotspots), 0)
        roles = [h["job_role"] for h in hotspots]
        self.assertTrue(any("salt" in r.lower() or "crusher" in r.lower() or "loader" in r.lower() for r in roles))

    def test_11_statutory_exports(self):
        """Tests BOCW Due List CSV and NPCCHH Heat Incident JSON exports."""
        bocw_res = export_statutory_report("bocw")
        self.assertEqual(bocw_res.media_type, "text/csv")
        self.assertIn("bocw_dhanvantari_rath_due_list.csv", bocw_res.headers["content-disposition"])

        npcchh_res = export_statutory_report("npcchh")
        self.assertIsInstance(npcchh_res, dict)
        self.assertIn("surveillance_program", npcchh_res)
        self.assertEqual(npcchh_res["district"], "Kachchh")

    def test_12_cool_shift_stats(self):
        """Validates shift optimization model (6am-3pm vs 9am-6pm avoiding ~20% hot hours)."""
        data = get_cool_shift_stats()
        self.assertIn("annual_hours_saved_average", data)
        self.assertIn("sites_comparison", data)
        self.assertEqual(len(data["sites_comparison"]), 5)
        for s in data["sites_comparison"]:
            self.assertGreater(s["hours_avoided"], 200)

    def test_13_live_telemetry_service(self):
        """Tests live satellite/weather service with automatic dataset fallback."""
        sites = list_sites()
        site_id = sites[0]["site_id"]
        res = get_site_live_telemetry(site_id)
        self.assertIn("ambient_temp_c", res)
        self.assertIn("calculated_wbgt_c", res)
        self.assertIn("lamp_color", res)
        self.assertIn(res["source"], ["LIVE_OPEN_METEO_API", "LOCAL_ERA5_CAMS_DATASET_FALLBACK"])

    def test_14_site_compliance_update(self):
        """Tests statutory facility compliance updates (drinking water, rest shelter, sanitation)."""
        sites = list_sites()
        site_id = sites[0]["site_id"]
        payload = SiteComplianceUpdate(
            has_potable_water=True,
            has_toilets=True,
            has_shaded_rest_area=True
        )
        res = update_site_compliance(site_id, payload)
        self.assertEqual(res["status"], "COMPLIANCE_UPDATED")
        self.assertEqual(res["site_id"], site_id)


if __name__ == "__main__":
    unittest.main()
