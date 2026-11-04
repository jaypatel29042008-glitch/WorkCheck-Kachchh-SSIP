import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.queries import OccupationalHealthQueries


def test_queries():
    queries = OccupationalHealthQueries()

    print("================================================================================")
    print("QUERY 1: WHO IS DUE FOR A CHECK-UP? (Top 5 Due List)")
    print("================================================================================")
    due_list = queries.get_workers_due_for_checkup(min_priority=4)
    print(f"Total Workers Flagged Due for Screening (Priority >= 4): {len(due_list)}")
    for w in due_list[:5]:
        print(f" - [{w['priority_score']}/5] {w['worker_name']} ({w['masked_eshram_uan']}) | Role: {w['job_role']}")
        print(f"   Site: {w['site_name']} ({w['taluka']}) | Facility: {w['assigned_facility']}")
        print(f"   Trigger: {w['flag_reason']}")
        print(f"   Heat Hrs > 30C: {w['recent_heat_hours_above_30c']}h | Dust Dose: {w['recent_dust_dose']} mg/m3*hr\n")

    print("================================================================================")
    print("QUERY 2: SITE RISK TODAY (Top 5 Highest WBGT Sites)")
    print("================================================================================")
    site_risks = queries.get_site_risk_today()
    print(f"Total Sites Assessed: {len(site_risks)}")
    for s in site_risks[:5]:
        water_flag = "ALERT: NO POTABLE WATER!" if not s['has_potable_water'] else "Potable Water OK"
        print(f" - [{s['current_lamp_color']}] {s['site_name']} ({s['taluka']}) | Type: {s['site_type']}")
        print(f"   WBGT: {s['current_wbgt_c']}°C | Ambient: {s['current_temp_c']}°C | Globe: {s['current_globe_temp_c']}°C | RH: {s['current_humidity_pct']}%")
        print(f"   Work-Rest Schedule: {s['required_work_rest_cycle']}")
        print(f"   Facilities: {water_flag} | Toilets: {bool(s['has_toilets'])} | Active Workers: {s['total_active_workers']}\n")

    print("================================================================================")
    print("QUERY 3: HOTSPOTS BY JOB ROLE")
    print("================================================================================")
    hotspots = queries.get_hotspots_by_job()
    for h in hotspots:
        print(f" - Job Role: {h['job_role'].upper()} (Workers: {h['worker_count']})")
        print(f"   Mean WBGT: {h['mean_wbgt_c']}°C | Total Hours > 30°C: {h['total_hours_above_30c']}h (Avg {h['avg_hours_above_30c_per_worker']}h/worker)")
        print(f"   Mean PM2.5: {h['mean_pm2_5_ug_m3']} ug/m3 | Peak PM2.5: {h['max_peak_pm2_5']} ug/m3 | Dust Dose: {h['mean_cumulative_dust_dose']} mg/m3*hr")
        print(f"   Screening Referral Rate: {h['screening_referral_pct']}% ({h['total_health_cases_triggered']} cases)")
        print(f"   Symptoms Reported: Dark Urine: {h['dark_urine_symptom_reports']} | Eye Glare: {h['eye_glare_symptom_reports']} | Cough: {h['respiratory_cough_reports']}\n")

    print("================================================================================")
    print("PRIVACY VIEW: ANONYMOUS DISTRICT HEAT & RISK SUMMARY")
    print("================================================================================")
    dist = queries.get_district_anonymous_summary()
    for d in dist:
        print(f" - Taluka: {d['taluka']:<12} | Type: {d['site_type']:<15} | Sites: {d['total_active_sites']:<2} | Workers: {d['total_monitored_workers']:<3}")
        print(f"   Mean WBGT: {d['mean_wbgt_c']}°C | Peak WBGT: {d['peak_wbgt_c']}°C | Total Hours > 30C: {d['total_hours_above_30c_wbgt']}h")
        print(f"   Overexposed Worker-Days: {d['total_overexposed_worker_days']} | Sites Lacking Water: {d['sites_lacking_drinking_water']}\n")


if __name__ == "__main__":
    test_queries()
