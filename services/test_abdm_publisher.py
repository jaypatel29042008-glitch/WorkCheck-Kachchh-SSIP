import unittest
import json
from services.abdm_publisher import ABDMPublisher


class TestABDMPublisher(unittest.TestCase):

    def setUp(self):
        self.publisher = ABDMPublisher()

    def test_build_and_publish_fhir_bundle(self):
        worker = {
            "worker_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
            "first_name": "Ramesh",
            "last_name": "Ahir",
            "gender": "Male",
            "age": 42,
            "eshram_uan": "100012345678",
            "abha_id": "91-4567-8901-2345",
            "abha_address": "ramesh.ahir@abdm",
            "phone_number": "+919825123456"
        }

        screening = {
            "doctor_registration_no": "GMC-KUTCH-MD-4081",
            "spirometry_fev1_liters": 2.10,
            "spirometry_fvc_liters": 3.40,
            "spirometry_fev1_fvc_ratio": 0.62, # < 0.70 (airway obstruction)
            "chest_xray_ilo_category": "1/1",  # Silicosis grade
            "serum_creatinine_mg_dl": 1.45,    # High (dehydration/kidney strain)
            "clinical_notes": "Suspected early silicosis and acute dehydration due to intense quarry dust exposure."
        }

        result = self.publisher.publish_to_abha(worker, screening)
        
        # Verify ABDM confirmation response
        resp = result["abdm_response"]
        self.assertEqual(resp["status"], "PUBLISHED_TO_ABHA_LOCKER")
        self.assertEqual(resp["worker_abha_address"], "ramesh.ahir@abdm")
        self.assertEqual(resp["worker_eshram_uan"], "100012345678")
        self.assertIn("CARE-CTX-", resp["care_context"]["referenceNumber"])
        self.assertEqual(len(resp["bundle_sha256"]), 64) # SHA-256 length

        # Verify FHIR R4 Bundle structure
        bundle = result["fhir_bundle"]
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "document")
        
        resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
        self.assertIn("Composition", resource_types)
        self.assertIn("Patient", resource_types)
        self.assertIn("Observation", resource_types)
        self.assertIn("DiagnosticReport", resource_types)

        # Check Patient identifiers
        patient = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient"][0]
        id_values = [i["value"] for i in patient["identifier"]]
        self.assertIn("91-4567-8901-2345", id_values)
        self.assertIn("100012345678", id_values)

        print("\nSUCCESS: FHIR R4 DiagnosticReport Bundle validated with ABHA & e-Shram UAN!")


if __name__ == "__main__":
    unittest.main()
