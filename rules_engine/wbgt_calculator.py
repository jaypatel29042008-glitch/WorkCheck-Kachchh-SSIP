"""
================================================================================
ISO 7243 WBGT & SENSOR CORRECTION ENGINE (PS000109)
================================================================================
Implements:
1. ISO 7243 Wet-Bulb Globe Temperature (WBGT) Calculation:
   - Direct Sensor Measurement (using 150 mm matte-black copper globe)
   - Liljegren & Bernard Meteorological Estimation (from Ta, RH, Solar, Wind)
2. ACGIH / ISO 7243 Work-Rest Schedules & Lamp Color Thresholds
3. PMS5003 Coastal Humidity Correction (Hygroscopic Aerosol Growth model)
================================================================================
"""

import math
from typing import Dict, Any, Tuple


class WBGTCalculator:
    """Calculates outdoor and indoor WBGT according to ISO 7243 standards."""

    @staticmethod
    def calculate_outdoor_wbgt(natural_wet_bulb_c: float, globe_temp_c: float, ambient_temp_c: float) -> float:
        """
        Direct sensor calculation for outdoor environments with direct solar load.
        Formula: WBGT_out = 0.7 * T_nw + 0.2 * T_g + 0.1 * T_a
        where:
          - T_nw: Natural wet-bulb temperature (°C)
          - T_g: 150 mm matte-black globe temperature (°C)
          - T_a: Ambient dry-bulb temperature in shade (°C)
        """
        return round(0.7 * natural_wet_bulb_c + 0.2 * globe_temp_c + 0.1 * ambient_temp_c, 2)

    @staticmethod
    def calculate_indoor_wbgt(natural_wet_bulb_c: float, globe_temp_c: float) -> float:
        """
        Direct sensor calculation for indoor or shaded environments (no direct solar radiation).
        Formula: WBGT_in = 0.7 * T_nw + 0.3 * T_g
        """
        return round(0.7 * natural_wet_bulb_c + 0.3 * globe_temp_c, 2)

    @staticmethod
    def estimate_natural_wet_bulb(ambient_temp_c: float, relative_humidity_pct: float) -> float:
        """
        Stull (2011) Empirical Formula for Wet-Bulb Temperature from dry bulb and relative humidity.
        Valid for Ta between -20°C and 50°C and RH between 5% and 99%.
        Accuracy: ±0.3°C.
        """
        T = ambient_temp_c
        RH = relative_humidity_pct

        tw = (
            T * math.atan(0.151977 * math.sqrt(RH + 8.313659))
            + math.atan(T + RH)
            - math.atan(RH - 1.676331)
            + 0.00391838 * (RH ** 1.5) * math.atan(0.023101 * RH)
            - 4.686035
        )
        return round(tw, 2)

    @staticmethod
    def estimate_globe_temp(
        ambient_temp_c: float,
        relative_humidity_pct: float,
        solar_radiation_w_m2: float = 800.0,
        wind_speed_m_s: float = 2.0
    ) -> float:
        """
        Estimates 150 mm standard matte-black globe temperature (ISO 7243)
        under solar irradiance and convective wind cooling.
        Based on heat balance: Convection + Radiation = Solar Absorption
        """
        v = max(wind_speed_m_s, 0.1)
        # Heat transfer coefficient for 150mm sphere: hc = 6.3 * (v^0.6) / (D^0.4)
        D = 0.15 # 150 mm diameter
        hc = 6.3 * (v ** 0.6) / (D ** 0.4)
        
        # Stefan-Boltzmann constant and globe emissivity
        epsilon = 0.95
        sigma = 5.67e-8
        
        # Approximate radiative equilibrium temperature increment
        delta_t = (0.95 * solar_radiation_w_m2) / (hc + 4 * epsilon * sigma * ((ambient_temp_c + 273.15) ** 3))
        tg = ambient_temp_c + delta_t
        return round(tg, 2)

    @classmethod
    def estimate_wbgt_from_weather(
        cls,
        ambient_temp_c: float,
        relative_humidity_pct: float,
        solar_radiation_w_m2: float = 750.0,
        wind_speed_m_s: float = 2.5
    ) -> Dict[str, float]:
        """
        Full meteorological estimation of WBGT when dedicated globe and wet-bulb sensors
        are not directly available.
        """
        tnw = cls.estimate_natural_wet_bulb(ambient_temp_c, relative_humidity_pct)
        tg = cls.estimate_globe_temp(ambient_temp_c, relative_humidity_pct, solar_radiation_w_m2, wind_speed_m_s)
        wbgt_out = cls.calculate_outdoor_wbgt(tnw, tg, ambient_temp_c)
        wbgt_in = cls.calculate_indoor_wbgt(tnw, tg)

        return {
            "ambient_temp_c": ambient_temp_c,
            "relative_humidity_pct": relative_humidity_pct,
            "estimated_wet_bulb_c": tnw,
            "estimated_globe_temp_c": tg,
            "wbgt_outdoor_c": wbgt_out,
            "wbgt_indoor_c": wbgt_in
        }

    @staticmethod
    def get_work_rest_cycle(wbgt_c: float, metabolic_rate: str = "HEAVY") -> Dict[str, Any]:
        """
        Returns the statutory ACGIH / ISO 7243 work-rest schedule and lamp command.
        Metabolic categories:
          - 'LIGHT' (Sitting, light manual work)
          - 'MODERATE' (Walking, scrubbing, lifting < 10kg)
          - 'HEAVY' (Salt raking, manual stone crushing, cement bag loading)
          - 'VERY_HEAVY' (Intense continuous physical exertion)
        """
        # Thresholds for HEAVY physical labor (Salt pan raking / Cement loading)
        if metabolic_rate.upper() in ["HEAVY", "VERY_HEAVY"]:
            if wbgt_c < 28.0:
                return {
                    "status": "NORMAL",
                    "lamp_color": "GREEN",
                    "work_pct": 100,
                    "rest_pct": 0,
                    "work_rest_minutes": "Continuous work (Standard hydration)",
                    "water_intake_recommendation_liters_per_hr": 0.5,
                    "action_required": "Maintain standard hydration; drink 1 glass of water every 30 mins."
                }
            elif wbgt_c < 29.5:
                return {
                    "status": "WARNING",
                    "lamp_color": "YELLOW",
                    "work_pct": 75,
                    "rest_pct": 25,
                    "work_rest_minutes": "45 min work / 15 min shaded rest per hour",
                    "water_intake_recommendation_liters_per_hr": 0.75,
                    "action_required": "Enforce mandatory 15-minute rest in shaded shelter; supervisor water check."
                }
            elif wbgt_c < 31.0:
                return {
                    "status": "DANGER",
                    "lamp_color": "ORANGE",
                    "work_pct": 50,
                    "rest_pct": 50,
                    "work_rest_minutes": "30 min work / 30 min shaded rest per hour",
                    "water_intake_recommendation_liters_per_hr": 1.0,
                    "action_required": "High heat stress risk! 30 mins work / 30 mins rest. Electrolyte ORS distribution."
                }
            else:
                return {
                    "status": "EMERGENCY",
                    "lamp_color": "RED",
                    "work_pct": 25,
                    "rest_pct": 75,
                    "work_rest_minutes": "15 min work / 45 min rest or STOP HEAVY WORK",
                    "water_intake_recommendation_liters_per_hr": 1.0,
                    "action_required": "CRITICAL RISK: Immediate stop of heavy manual labor. Move workers to shade. Risk of heat stroke!"
                }
        else: # MODERATE / LIGHT
            if wbgt_c < 30.0:
                return {"status": "NORMAL", "lamp_color": "GREEN", "work_pct": 100, "rest_pct": 0, "work_rest_minutes": "Continuous work"}
            elif wbgt_c < 31.5:
                return {"status": "WARNING", "lamp_color": "YELLOW", "work_pct": 75, "rest_pct": 25, "work_rest_minutes": "45m work / 15m rest"}
            elif wbgt_c < 32.5:
                return {"status": "DANGER", "lamp_color": "ORANGE", "work_pct": 50, "rest_pct": 50, "work_rest_minutes": "30m work / 30m rest"}
            else:
                return {"status": "EMERGENCY", "lamp_color": "RED", "work_pct": 25, "rest_pct": 75, "work_rest_minutes": "15m work / 45m rest or stop"}


class SensorCorrection:
    """
    Sensor corrections for low-cost hardware in coastal and industrial environments.
    Addresses findings from Scientific Reports 2022 & AQICN PMS5003 research.
    """

    @staticmethod
    def correct_pms5003_humidity(pm_raw_ug_m3: float, relative_humidity_pct: float) -> float:
        """
        Corrects for hygroscopic growth of aerosol particles in high humidity (> 60% RH).
        In coastal Kachchh (Mundra, Kandla), ambient air often exceeds 75% RH.
        Cheap optical particle counters mistake swelling water droplets for heavy dust.
        
        Formula:
          PM_corrected = PM_raw / (1 + kappa * (RH^2 / (1 - RH)))
          where RH is fraction [0, 1) and kappa = 0.25 (calibrated for coastal salt/mineral dust).
        """
        if relative_humidity_pct <= 60.0 or pm_raw_ug_m3 <= 0:
            return round(pm_raw_ug_m3, 2)
        
        # Cap RH at 98% to prevent division by zero
        rh_frac = min(relative_humidity_pct / 100.0, 0.98)
        growth_factor = 1.0 + 0.25 * ((rh_frac ** 2) / (1.0 - rh_frac))
        corrected_pm = pm_raw_ug_m3 / growth_factor
        return round(max(corrected_pm, 0.0), 2)

    @staticmethod
    def evaluate_150mm_globe_vs_pingpong(pingpong_40mm_temp_c: float, wind_speed_m_s: float) -> float:
        """
        Correction polynomial if an existing site is still temporarily using a 40 mm ping-pong ball
        until upgraded to the standard 150 mm matte-black copper globe.
        (Scientific Reports 2022 finding: 40mm ball underestimates true radiant heat under wind).
        """
        v = max(wind_speed_m_s, 0.2)
        # Empirical wind-loss compensation factor
        wind_compensation = 1.8 * (v ** 0.4)
        estimated_standard_globe = pingpong_40mm_temp_c + wind_compensation
        return round(estimated_standard_globe, 2)
