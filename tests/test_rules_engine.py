"""
Unit tests for ISO 7243 WBGT Calculation, Humidity Correction, and Rules Engine.
"""

import unittest
from datetime import date
from rules_engine.wbgt_calculator import WBGTCalculator, SensorCorrection
from rules_engine.rules_evaluator import RulesEvaluator


class TestWBGTCalculator(unittest.TestCase):

    def test_outdoor_wbgt_formula(self):
        # Ta = 35.0, Tg = 50.0 (under sun), Tnw = 28.0
        # Expected: 0.7 * 28 + 0.2 * 50 + 0.1 * 35 = 19.6 + 10.0 + 3.5 = 33.1
        wbgt = WBGTCalculator.calculate_outdoor_wbgt(
            natural_wet_bulb_c=28.0,
            globe_temp_c=50.0,
            ambient_temp_c=35.0
        )
        self.assertAlmostEqual(wbgt, 33.1, places=1)

    def test_indoor_wbgt_formula(self):
        # Tnw = 26.0, Tg = 30.0 (in shade/indoor)
        # Expected: 0.7 * 26 + 0.3 * 30 = 18.2 + 9.0 = 27.2
        wbgt = WBGTCalculator.calculate_indoor_wbgt(
            natural_wet_bulb_c=26.0,
            globe_temp_c=30.0
        )
        self.assertAlmostEqual(wbgt, 27.2, places=1)

    def test_work_rest_schedules(self):
        # Under 28°C: GREEN, continuous work
        cycle_green = WBGTCalculator.get_work_rest_cycle(26.5, "HEAVY")
        self.assertEqual(cycle_green["lamp_color"], "GREEN")
        self.assertEqual(cycle_green["work_pct"], 100)

        # 28°C - 29.5°C: YELLOW (75% work / 25% rest)
        cycle_yellow = WBGTCalculator.get_work_rest_cycle(28.8, "HEAVY")
        self.assertEqual(cycle_yellow["lamp_color"], "YELLOW")
        self.assertEqual(cycle_yellow["work_pct"], 75)

        # 29.5°C - 31.0°C: ORANGE (50% work / 50% rest)
        cycle_orange = WBGTCalculator.get_work_rest_cycle(30.2, "HEAVY")
        self.assertEqual(cycle_orange["lamp_color"], "ORANGE")
        self.assertEqual(cycle_orange["work_pct"], 50)

        # >= 31.0°C: RED (Emergency / 15m work / 45m rest)
        cycle_red = WBGTCalculator.get_work_rest_cycle(32.0, "HEAVY")
        self.assertEqual(cycle_red["lamp_color"], "RED")
        self.assertEqual(cycle_red["work_pct"], 25)

    def test_pms5003_humidity_correction(self):
        # Below 60% RH: No correction applied
        raw_pm = 80.0
        corrected_low_rh = SensorCorrection.correct_pms5003_humidity(raw_pm, 50.0)
        self.assertEqual(corrected_low_rh, 80.0)

        # High humidity (85% RH in coastal Mundra): Growth factor suppresses spurious optical sizing
        corrected_high_rh = SensorCorrection.correct_pms5003_humidity(raw_pm, 85.0)
        self.assertLess(corrected_high_rh, raw_pm)
        # Factor = 1 + 0.25 * (0.85^2 / 0.15) = 1 + 0.25 * 4.816 = ~2.204
        # 80 / 2.204 = ~36.3 ug/m3
        self.assertAlmostEqual(corrected_high_rh, 36.3, delta=2.0)


class TestRulesEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = RulesEvaluator()

    def test_realtime_heat_alert_and_lamp(self):
        # Test extreme heat reading
        res = self.evaluator.evaluate_realtime_reading(
            site_id="SITE-001",
            device_id="DEV-001",
            ambient_temp_c=38.0,
            relative_humidity_pct=70.0,
            raw_pm2_5_ug_m3=45.0
        )
        self.assertIn(res["lamp_color"], ["ORANGE", "RED"])
        self.assertTrue(len(res["alerts"]) > 0)
        heat_alerts = [a for a in res["alerts"] if a["hazard"] == "HEAT"]
        self.assertEqual(len(heat_alerts), 1)
        self.assertIn("WBGT", heat_alerts[0]["message_en"])
        self.assertIn("ગરમી", heat_alerts[0]["message_gu"]) # Gujarati check

    def test_daily_exposure_cumulative_dust_trigger(self):
        # 30-day cumulative dose exceeds 2.5 mg/m³·hr
        res = self.evaluator.evaluate_daily_worker_exposure(
            worker_id="WORKER-001",
            site_id="SITE-001",
            shift_date=date.today(),
            shift_duration_hours=8.0,
            avg_pm2_5_ug_m3=180.0, # 180 ug/m3 = 0.180 mg/m3
            peak_pm2_5_ug_m3=350.0,
            avg_wbgt_c=27.5,
            max_wbgt_c=28.5,
            hours_above_wbgt_28=1.0,
            hours_above_wbgt_30=0.0,
            consecutive_dark_urine_days=0,
            thirty_day_cumulative_dust_dose=2.4 # adding 0.180*8 = 1.44 -> total > 3.8
        )
        self.assertTrue(res["flag_over_exposure"])
        self.assertIsNotNone(res["recommended_case"])
        self.assertEqual(res["recommended_case"]["case_type"], "DUST_SILICOSIS_SUSPECT")
        self.assertEqual(res["recommended_case"]["assigned_facility"], "Gujarat BOCW Dhanvantari Rath")


if __name__ == "__main__":
    unittest.main()
