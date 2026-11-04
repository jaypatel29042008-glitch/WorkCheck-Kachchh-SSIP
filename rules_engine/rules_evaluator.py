"""
================================================================================
MULTI-HAZARD OCCUPATIONAL RULES ENGINE (PS000109)
================================================================================
Orchestrates:
1. Heat Stress Evaluation (ISO 7243 WBGT -> Lamp colors + Hydration SMS)
2. Respirable Dust / Crystalline Silica Dose Evaluation (Action Level > 25 ug/m3, PEL > 50 ug/m3)
3. Dehydration & Multi-Symptom Screening Triggers (Dark urine + Dizziness -> Acute Kidney Risk)
4. Site Facility Adequacy Audits (Missing drinking water or toilets on active sites)
5. Automated Health Van Due List Scheduling (BOCW Rath, Salt Pan Van, ESIC)
================================================================================
"""

import uuid
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from rules_engine.wbgt_calculator import WBGTCalculator, SensorCorrection


class RulesEvaluator:
    """Evaluates occupational safety rules against real-time telemetry and worker histories."""

    def __init__(self, db_connection=None):
        self.con = db_connection

    def evaluate_realtime_reading(
        self,
        site_id: str,
        device_id: str,
        ambient_temp_c: float,
        relative_humidity_pct: float,
        globe_temp_c: Optional[float] = None,
        natural_wet_bulb_c: Optional[float] = None,
        raw_pm2_5_ug_m3: Optional[float] = None,
        uv_index: Optional[float] = None,
        worker_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a real-time sensor reading from an ESP32 site node or dust badge.
        Returns computed WBGT, corrected PM, lamp color, and generated alerts.
        """
        # 1. Apply Coastal Humidity Correction to Dust
        corrected_pm2_5 = None
        if raw_pm2_5_ug_m3 is not None:
            corrected_pm2_5 = SensorCorrection.correct_pms5003_humidity(
                raw_pm2_5_ug_m3, relative_humidity_pct
            )

        # 2. Compute WBGT (using direct sensors if available, else Stull estimation)
        if natural_wet_bulb_c is not None and globe_temp_c is not None:
            wbgt_c = WBGTCalculator.calculate_outdoor_wbgt(
                natural_wet_bulb_c, globe_temp_c, ambient_temp_c
            )
        else:
            weather_wbgt = WBGTCalculator.estimate_wbgt_from_weather(
                ambient_temp_c, relative_humidity_pct
            )
            wbgt_c = weather_wbgt["wbgt_outdoor_c"]
            globe_temp_c = weather_wbgt["estimated_globe_temp_c"]
            natural_wet_bulb_c = weather_wbgt["estimated_wet_bulb_c"]

        # 3. Determine Work-Rest Schedule and Site Lamp Color
        work_rest = WBGTCalculator.get_work_rest_cycle(wbgt_c, metabolic_rate="HEAVY")
        lamp_color = work_rest["lamp_color"]

        alerts = []

        # 4. Heat Stress Alert Trigger
        if lamp_color in ["ORANGE", "RED"]:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "site_id": site_id,
                "device_id": device_id,
                "worker_id": worker_id,
                "severity": "CRITICAL" if lamp_color == "RED" else "WARNING",
                "hazard": "HEAT",
                "lamp_color": lamp_color,
                "message_en": f"CRITICAL HEAT STRESS (WBGT {wbgt_c}°C): Enforce {work_rest['work_rest_minutes']}. Ensure ORS electrolyte intake.",
                "message_gu": f"ચેતવણી: અતિશય ગરમી (WBGT {wbgt_c}°C)! તાત્કાલિક {work_rest['work_rest_minutes']} અમલમાં મૂકો. પીવાનું પાણી અને ORS આપો.",
                "message_hi": f"चेतावनी: अत्यधिक गर्मी (WBGT {wbgt_c}°C)! तुरंत {work_rest['work_rest_minutes']} लागू करें। ओआरएस और पानी पिएं।"
            })

        # 5. Acute Particulate Spike Trigger (PM2.5 > 250 ug/m3 in crusher/cement zones)
        if corrected_pm2_5 is not None and corrected_pm2_5 > 250.0:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "site_id": site_id,
                "device_id": device_id,
                "worker_id": worker_id,
                "severity": "WARNING",
                "hazard": "DUST",
                "lamp_color": "ORANGE",
                "message_en": f"HAZARDOUS DUST SPIKE (PM2.5: {corrected_pm2_5} µg/m³): Mandatory N95/dust respirator check and water-spray misting required.",
                "message_gu": f"ધૂળનું જોખમી સ્તર (PM2.5: {corrected_pm2_5} µg/m³)! તાત્કાલિક ડસ્ટ માસ્ક પહેરો અને પાણીનો છંટકાવ કરો.",
                "message_hi": f"धूल का खतरनाक स्तर (PM2.5: {corrected_pm2_5} µg/m³)! मास्क पहनना अनिवार्य है और पानी का छिड़काव करें।"
            })

        # 6. UV Radiation Warning (for Salt-Pan workers on white crystalline salt)
        if uv_index is not None and uv_index >= 8.0:
            alerts.append({
                "alert_id": str(uuid.uuid4()),
                "site_id": site_id,
                "device_id": device_id,
                "worker_id": worker_id,
                "severity": "INFO",
                "hazard": "UV_GLARE",
                "lamp_color": lamp_color,
                "message_en": f"HIGH UV INDEX ({uv_index}) ON SALT PAN: Severe eye glare risk. Ensure protective UV sunglasses/goggles are worn.",
                "message_gu": f"મીઠાના અગરમાં સૂર્યનો આકરો તડકો (UV: {uv_index})! આંખોના રક્ષણ માટે કાળા ચશ્મા (ગોગલ્સ) પહેરવા જરૂરી છે.",
                "message_hi": f"नमक के मैदान में तीव्र यूवी किरणें (UV: {uv_index})! आंखों की सुरक्षा के लिए चश्मा पहनना जरूरी है।"
            })

        return {
            "site_id": site_id,
            "calculated_wbgt_c": wbgt_c,
            "globe_temp_c": globe_temp_c,
            "natural_wet_bulb_c": natural_wet_bulb_c,
            "corrected_pm2_5_ug_m3": corrected_pm2_5,
            "lamp_color": lamp_color,
            "work_rest_schedule": work_rest,
            "alerts": alerts
        }

    @staticmethod
    def evaluate_daily_worker_exposure(
        worker_id: str,
        site_id: str,
        shift_date: date,
        shift_duration_hours: float,
        avg_pm2_5_ug_m3: float,
        peak_pm2_5_ug_m3: float,
        avg_wbgt_c: float,
        max_wbgt_c: float,
        hours_above_wbgt_28: float,
        hours_above_wbgt_30: float,
        consecutive_dark_urine_days: int = 0,
        thirty_day_cumulative_dust_dose: float = 0.0,
        has_drinking_water: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates nightly aggregated exposure against clinical screening triggers:
        1. Silica Dust Action Level Trigger (> 2.5 mg/m³·hr cumulative) -> Spirometry & Chest X-Ray
        2. Chronic Heat & Dehydration Trigger (> 15 hours > 30°C + dark urine) -> Creatinine & Van Referral
        3. Site Infrastructure Violation (Working in extreme heat without potable water)
        """
        # Calculate daily dust dose (mg/m3 * hr)
        daily_dust_dose = (avg_pm2_5_ug_m3 / 1000.0) * shift_duration_hours
        updated_cumulative_dust = thirty_day_cumulative_dust_dose + daily_dust_dose

        flag_over_exposure = False
        reasons = []
        recommended_case_type = None
        priority_score = 1
        assigned_facility = None

        # Rule 1: Cumulative Dust Threshold (Silica exposure in quarries/cement/crushers)
        # Indian Factories Act Sec 41C & OSHA PEL Action Level:
        # If 30-day cumulative dose exceeds 2.5 mg/m³·hr
        if updated_cumulative_dust >= 2.5:
            flag_over_exposure = True
            reasons.append(f"30-day cumulative dust dose ({updated_cumulative_dust:.2f} mg/m³·hr) exceeded occupational limit.")
            recommended_case_type = "DUST_SILICOSIS_SUSPECT"
            priority_score = max(priority_score, 4)
            assigned_facility = "Gujarat BOCW Dhanvantari Rath"

        # Rule 2: Chronic Heat + Dehydration (Salt pan nephropathy / CKDu prevention)
        # Based on Tamil Nadu Salt Pan findings (Dr. Vidhya Venugopal)
        if hours_above_wbgt_30 >= 3.0 and consecutive_dark_urine_days >= 2:
            flag_over_exposure = True
            reasons.append(f"Severe heat strain: {hours_above_wbgt_30:.1f} hrs > 30°C WBGT with {consecutive_dark_urine_days} days dark urine (kidney risk).")
            recommended_case_type = "HEAT_NEPHROPATHY_SUSPECT"
            priority_score = max(priority_score, 5)
            assigned_facility = "Salt-Worker Medical Van"

        # Rule 3: Site Sanitation / Water Violation
        if not has_drinking_water and max_wbgt_c >= 29.5:
            flag_over_exposure = True
            reasons.append("Statutory Violation: Active work site lacks potable water during high heat conditions (WBGT >= 29.5°C).")
            priority_score = max(priority_score, 3)

        return {
            "worker_id": worker_id,
            "site_id": site_id,
            "shift_date": str(shift_date),
            "daily_dust_dose_mg_m3_hr": round(daily_dust_dose, 3),
            "cumulative_30d_dust_dose_mg_m3_hr": round(updated_cumulative_dust, 3),
            "flag_over_exposure": flag_over_exposure,
            "flag_reason": "; ".join(reasons) if reasons else "Normal exposure within permissible limits.",
            "recommended_case": {
                "case_id": str(uuid.uuid4()),
                "case_type": recommended_case_type,
                "priority_score": priority_score,
                "assigned_facility": assigned_facility,
                "status": "PENDING_SCREENING"
            } if recommended_case_type else None
        }
