"""
================================================================================
OCCUPATIONAL HEALTH QUERY CONTRACTS (PS000109)
================================================================================
Implements the core analytical and operational queries required by:
1. Person 3 (FastAPI Endpoints & BOCW / ESIC exports)
2. Person 4 (Pitch evidence & district heat/dust visualizations)
3. District Mobile Medical Vans (Route planning and priority scheduling)
================================================================================
"""

import sqlite3
from typing import List, Dict, Any, Optional


class OccupationalHealthQueries:
    """Production query interface for occupational health database."""

    def __init__(self, db_path: str = r"c:\Users\jaypa\OneDrive\Documents\SSIP\database\occupational_health.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def get_workers_due_for_checkup(self, taluka: Optional[str] = None, min_priority: int = 1) -> List[Dict[str, Any]]:
        """
        Query 1: 'Who's due for a check-up'
        Identifies workers requiring clinical screening based on:
          1. Over-exposure trigger (cumulative silica dust or severe heat strain)
          2. Reported persistent clinical symptoms (dark urine, dizziness, cough)
          3. Statutory annual requirement (> 365 days since last checkup under OSH Code 2020)
        Respects worker consent: Only includes workers with consent_given = TRUE.
        """
        con = self._get_connection()
        cursor = con.cursor()

        query = """
        SELECT 
            w.worker_id,
            SUBSTR(w.eshram_uan, 1, 4) || '-XXXX-' || SUBSTR(w.eshram_uan, 9, 4) AS masked_eshram_uan,
            w.abha_address,
            w.first_name || ' ' || w.last_name AS worker_name,
            w.age,
            w.gender,
            w.job_role,
            s.site_name,
            s.taluka,
            s.has_potable_water,
            c.case_id,
            c.case_type,
            c.priority_score,
            c.status AS case_status,
            c.assigned_facility,
            COALESCE(de.cumulative_dust_dose_mg_m3_hr, 0.0) AS recent_dust_dose,
            COALESCE(de.hours_above_wbgt_30, 0.0) AS recent_heat_hours_above_30c,
            de.flag_reason
        FROM workers w
        JOIN sites s ON w.current_site_id = s.site_id
        JOIN cases c ON w.worker_id = c.worker_id
        LEFT JOIN daily_exposure de ON w.worker_id = de.worker_id 
             AND de.shift_date = (SELECT MAX(shift_date) FROM daily_exposure WHERE worker_id = w.worker_id)
        WHERE w.consent_given = 1
          AND w.is_active = 1
          AND c.status IN ('PENDING_SCREENING', 'VAN_SCHEDULED')
          AND c.priority_score >= ?
        """
        params = [min_priority]

        if taluka:
            query += " AND s.taluka = ?"
            params.append(taluka)

        query += " ORDER BY c.priority_score DESC, de.hours_above_wbgt_30 DESC;"

        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        con.close()
        return results

    def get_site_risk_today(self, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query 2: 'Site risk today'
        Calculates real-time / current-day risk metrics for worksites:
          - WBGT level & current lamp color (GREEN/YELLOW/ORANGE/RED)
          - Corrected PM2.5 levels
          - Required ISO 7243 work-rest schedule
          - Infrastructure adequacy (Drinking water & toilet flags)
          - Total workers on-site and percentage under heat strain
        """
        con = self._get_connection()
        cursor = con.cursor()

        query = """
        SELECT 
            s.site_id,
            s.site_name,
            s.site_type,
            s.taluka,
            s.latitude,
            s.longitude,
            s.has_potable_water,
            s.has_toilets,
            s.has_shaded_rest_area,
            COUNT(DISTINCT w.worker_id) AS total_active_workers,
            ROUND(AVG(r.ambient_temp_c), 1) AS current_temp_c,
            ROUND(AVG(r.relative_humidity_pct), 1) AS current_humidity_pct,
            ROUND(AVG(r.globe_temp_c), 1) AS current_globe_temp_c,
            ROUND(AVG(r.calculated_wbgt_c), 1) AS current_wbgt_c,
            ROUND(AVG(r.pm2_5_ug_m3), 1) AS current_pm2_5_ug_m3,
            ROUND(AVG(r.uv_index), 1) AS current_uv_index,
            CASE 
                WHEN AVG(r.calculated_wbgt_c) >= 31.0 THEN 'RED'
                WHEN AVG(r.calculated_wbgt_c) >= 29.5 THEN 'ORANGE'
                WHEN AVG(r.calculated_wbgt_c) >= 28.0 THEN 'YELLOW'
                ELSE 'GREEN'
            END AS current_lamp_color,
            CASE 
                WHEN AVG(r.calculated_wbgt_c) >= 31.0 THEN '15 min work / 45 min rest or STOP HEAVY WORK'
                WHEN AVG(r.calculated_wbgt_c) >= 29.5 THEN '30 min work / 30 min rest in shade'
                WHEN AVG(r.calculated_wbgt_c) >= 28.0 THEN '45 min work / 15 min rest in shade'
                ELSE 'Continuous work (Hydrate regularly)'
            END AS required_work_rest_cycle,
            CASE WHEN s.has_potable_water = 0 AND AVG(r.calculated_wbgt_c) >= 29.5 THEN 1 ELSE 0 END AS water_violation_flag
        FROM sites s
        LEFT JOIN workers w ON s.site_id = w.current_site_id AND w.is_active = 1
        LEFT JOIN readings r ON s.site_id = r.site_id 
             AND r.recorded_at >= datetime('now', '-4 hours')
        """
        params = []
        if site_id:
            query += " WHERE s.site_id = ?"
            params.append(site_id)

        query += " GROUP BY s.site_id, s.site_name, s.site_type, s.taluka ORDER BY current_wbgt_c DESC;"

        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        con.close()
        return results

    def get_hotspots_by_job(self) -> List[Dict[str, Any]]:
        """
        Query 3: 'Hotspots by job'
        Aggregates occupational hazards across job roles:
          - Salt Rakers: High WBGT, direct solar UV glare, brine contact
          - Crusher Operators & Cement Loaders: High respirable silica PM2.5/PM10
          - Heavy Equipment / Truck Drivers: Whole-body vibration + heat
        """
        con = self._get_connection()
        cursor = con.cursor()

        query = """
        SELECT 
            w.job_role,
            COUNT(DISTINCT w.worker_id) AS worker_count,
            COUNT(DISTINCT w.current_site_id) AS distinct_sites_count,
            ROUND(AVG(de.avg_pm2_5_ug_m3), 2) AS mean_pm2_5_ug_m3,
            ROUND(MAX(de.peak_pm2_5_ug_m3), 2) AS max_peak_pm2_5,
            ROUND(AVG(de.cumulative_dust_dose_mg_m3_hr), 3) AS mean_cumulative_dust_dose,
            ROUND(AVG(de.avg_wbgt_c), 2) AS mean_wbgt_c,
            ROUND(SUM(de.hours_above_wbgt_30), 1) AS total_hours_above_30c,
            ROUND(AVG(de.hours_above_wbgt_30), 2) AS avg_hours_above_30c_per_worker,
            COUNT(DISTINCT c.case_id) AS total_health_cases_triggered,
            ROUND(CAST(COUNT(DISTINCT c.case_id) AS FLOAT) * 100.0 / COUNT(DISTINCT w.worker_id), 1) AS screening_referral_pct,
            SUM(CASE WHEN sym.dark_urine = 1 THEN 1 ELSE 0 END) AS dark_urine_symptom_reports,
            SUM(CASE WHEN sym.eye_burning_salt_glare = 1 THEN 1 ELSE 0 END) AS eye_glare_symptom_reports,
            SUM(CASE WHEN sym.persistent_cough = 1 THEN 1 ELSE 0 END) AS respiratory_cough_reports
        FROM workers w
        LEFT JOIN daily_exposure de ON w.worker_id = de.worker_id
        LEFT JOIN cases c ON w.worker_id = c.worker_id
        LEFT JOIN symptoms sym ON w.worker_id = sym.worker_id
        WHERE w.is_active = 1
        GROUP BY w.job_role
        ORDER BY screening_referral_pct DESC, total_hours_above_30c DESC;
        """

        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        con.close()
        return results

    def get_district_anonymous_summary(self) -> List[Dict[str, Any]]:
        """
        Privacy-Preserving District View (DPDP Act 2023 Compliant)
        Allows district officials (DDO Kachchh, Chief District Health Officer)
        to see high-level hazard heatmaps without accessing individual identities.
        """
        con = self._get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM district_taluka_heat_summary;")
        results = [dict(row) for row in cursor.fetchall()]
        con.close()
        return results
