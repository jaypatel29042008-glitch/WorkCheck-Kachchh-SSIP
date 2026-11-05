"""
================================================================================
PS000109: GENERATE MISSING DATASET FILES & CLINICAL EXTENSIONS
================================================================================
Generates all 9 dataset files specified in missing_files_checklist.txt:
1. sim_bme280_breath_telemetry.csv (Mentor's mask respiration experiment)
2. sim_rfid_qr_checkin_logs.csv (Attendance, 55+ hr work-week trigger)
3. sensor_calibration_curves.csv (Hardware transfer functions & instruments)
4. sim_clinical_test_records.csv (Spirometry, ILO CXR, Creatinine, Audiogram)
5. statutory_fitness_forms.csv (Gujarat Rule 9 Form 5 & Central Form VIII)
6. health_facilities_kachchh.csv (Kachchh PHC/CHC/Hospital diagnostic network)
7. unregistered_worker_enrollment.csv (Untracked worker onboarding at van)
8. worker_consent_audit_log.csv (3-tier DPDP Act 2023 audit ledger)
9. local_silica_lab_assays.csv (NIOH Ahmedabad regional XRD quartz % assays)
================================================================================
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_ROOT / "data" / "tables"
SIM_DIR = PROJECT_ROOT / "data" / "simulation"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
SIM_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# Existing worker IDs from database
WORKER_IDS = [f"W-KCH-{i:04d}" for i in range(1, 51)]
SITES = ["bhuj_hq", "mundra_port", "kandla_dock", "little_rann_salt", "abdasa_cement", "anjar_steel"]

# ------------------------------------------------------------------------------
# 1. sim_bme280_breath_telemetry.csv
# ------------------------------------------------------------------------------
def generate_bme280_telemetry():
    file_path = SIM_DIR / "sim_bme280_breath_telemetry.csv"
    headers = [
        "timestamp", "worker_id", "temperature_c", "relative_humidity_pct",
        "pressure_hpa", "respiratory_rate_bpm", "mask_donned_flag",
        "minute_ventilation_est_l_min", "condensation_clog_flag"
    ]
    rows = []
    base_time = datetime(2025, 5, 10, 8, 0, 0)
    for worker_id in WORKER_IDS[:15]:  # Pilot cohort of 15 workers
        donned = random.choice([True, True, True, False])
        for step in range(20):  # 20 readings per worker
            t = base_time + timedelta(minutes=step * 15)
            if donned:
                temp = round(random.uniform(33.5, 36.8), 2)
                rh = round(random.uniform(82.0, 96.5), 1)
                bpm = round(random.uniform(16.0, 26.5), 1)
                ve = round(bpm * random.uniform(0.7, 1.2), 2)
                clog = rh > 94.0 and random.random() < 0.15
            else:
                temp = round(random.uniform(37.0, 41.5), 2)
                rh = round(random.uniform(45.0, 65.0), 1)
                bpm = round(random.uniform(14.0, 18.0), 1)
                ve = round(bpm * 0.5, 2)
                clog = False
            
            rows.append([
                t.isoformat(), worker_id, temp, rh,
                round(random.uniform(1004.0, 1012.0), 1),
                bpm, donned, ve, clog
            ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 2. sim_rfid_qr_checkin_logs.csv
# ------------------------------------------------------------------------------
def generate_rfid_qr_logs():
    file_path = SIM_DIR / "sim_rfid_qr_checkin_logs.csv"
    headers = [
        "log_id", "worker_id", "node_id", "site_id", "timestamp",
        "event_type", "scan_method", "weekly_accumulated_hours", "consecutive_weeks_over_55"
    ]
    rows = []
    log_counter = 10001
    base_date = datetime(2025, 5, 1)

    for worker_id in WORKER_IDS:
        site = random.choice(SITES)
        weekly_hrs = round(random.uniform(42.0, 68.0), 1)
        over_55_weeks = 3 if weekly_hrs > 58.0 else (1 if weekly_hrs > 54.0 else 0)
        
        for day in range(7):
            dt = base_date + timedelta(days=day)
            # Check-in
            rows.append([
                f"LOG-{log_counter}", worker_id, f"NODE-{site[:4].upper()}-01", site,
                (dt.replace(hour=7, minute=random.randint(45, 59))).isoformat(),
                "CHECK_IN", random.choice(["RFID_CARD", "QR_CODE"]),
                weekly_hrs, over_55_weeks
            ])
            log_counter += 1
            # Check-out
            rows.append([
                f"LOG-{log_counter}", worker_id, f"NODE-{site[:4].upper()}-01", site,
                (dt.replace(hour=16, minute=random.randint(0, 30))).isoformat(),
                "CHECK_OUT", random.choice(["RFID_CARD", "QR_CODE"]),
                weekly_hrs, over_55_weeks
            ])
            log_counter += 1

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 3. sensor_calibration_curves.csv
# ------------------------------------------------------------------------------
def generate_calibration_curves():
    file_path = TABLES_DIR / "sensor_calibration_curves.csv"
    headers = [
        "sensor_part", "parameter_tracked", "raw_unit", "physical_unit",
        "transfer_formula", "reference_instrument", "error_tolerance_pct"
    ]
    rows = [
        ["Plantower PMS5003", "Respirable PM2.5", "RAW_PULSE_COUNTS", "ug/m3", "pm25_corr = pm25_raw / (1 + 0.24 * (RH/100)^2 / (1 - RH/100))", "Grimm 11-D Optical Particle Counter", 8.5],
        ["BME280 Mask Probe", "Respiration Rate / Exhaled RH", "I2C_RH_TEMP", "breaths_per_minute", "peak_detection(delta_rh > 4.5% in 1.2s window)", "Jaeger Oxycon Spirometer", 5.2],
        ["150mm Matte-Black Globe", "Mean Radiant Temperature (Tg)", "PT100_RESISTANCE", "deg_C", "Tg = (R - 100) / 0.385", "Casella 150mm Copper Standard Globe", 2.0],
        ["Natural Wet Bulb Wick", "Natural Wet Bulb (Tnw)", "NTC_10K_VOLTAGE", "deg_C", "Steinhart-Hart equation (distilled water wick, naturally ventilated)", "Assmann Aspirated Psychrometer", 3.1],
        ["GUVA-S12SD", "Solar UV Index", "ANALOG_MILLIVOLTS", "UV_INDEX_1_12", "UVI = mV / 100.0", "Yankee Environmental Systems UVB-1", 7.0],
        ["INMP441 Microphone", "A-weighted Noise Dose", "I2S_DIGITAL_AUDIO", "dBA_SPL", "dBA = 20 * log10(RMS / 20uPa) + A_weighting_filter()", "Bruel & Kjaer 2250 Type 1 Sound Level Meter", 4.0],
        ["TCS34725 Colorimeter", "Hydration Color Scale", "RGB_CLEAR_CHANNEL", "ARMSTRONG_SCALE_1_8", "classify_rgb_euclidean(R, G, B, armstrong_centroids)", "Konica Minolta CM-700d Spectrophotometer", 6.5]
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 4. sim_clinical_test_records.csv
# ------------------------------------------------------------------------------
def generate_clinical_records():
    file_path = SIM_DIR / "sim_clinical_test_records.csv"
    headers = [
        "test_id", "worker_id", "screening_date", "facility_id", "doctor_registration_no",
        "fev1_litres", "fvc_litres", "fev1_fvc_ratio", "fev1_pct_predicted",
        "cxr_ilo_profusion", "cxr_opacities_shape", "serum_creatinine_mg_dl", "egfr_ckd_epi",
        "urine_specific_gravity", "urine_protein_dipstick", "spo2_pct", "resting_pulse_bpm",
        "systolic_bp_mmhg", "diastolic_bp_mmhg", "pta_hearing_threshold_db_4khz",
        "sputum_cbnaat_result", "clinical_verdict", "fitness_certificate_status"
    ]
    rows = []
    facilities = ["FAC-BHUJ-GK", "FAC-MUNDRA-CHC", "FAC-GANDHI-ESIC", "FAC-MOB-VAN-01", "FAC-MOB-VAN-02"]
    
    for i, worker_id in enumerate(WORKER_IDS):
        fvc = round(random.uniform(3.2, 4.4), 2)
        is_dusty_quarry = (i % 3 == 0)
        is_salt_dehydrated = (i % 4 == 0)

        if is_dusty_quarry:
            fev1 = round(fvc * random.uniform(0.58, 0.68), 2)
            ratio = round(fev1 / fvc, 2)
            fev1_pct = round(random.uniform(62.0, 74.0), 1)
            ilo = random.choice(["1/0", "1/1", "1/2"])
            opacities = "q"
            verdict = "SUSPECTED_SILICOSIS"
            cert = "FIT_WITH_RESTRICTION"
        else:
            fev1 = round(fvc * random.uniform(0.74, 0.86), 2)
            ratio = round(fev1 / fvc, 2)
            fev1_pct = round(random.uniform(84.0, 102.0), 1)
            ilo = "0/0"
            opacities = "-"
            verdict = "NORMAL"
            cert = "FIT"

        if is_salt_dehydrated:
            creat = round(random.uniform(1.35, 1.85), 2)
            egfr = round(random.uniform(48.0, 68.0), 1)
            usg = round(random.uniform(1.026, 1.034), 3)
            protein = random.choice(["1+", "2+"])
            if verdict == "NORMAL":
                verdict = "CKD_HEAT_STRESS_RISK"
        else:
            creat = round(random.uniform(0.85, 1.15), 2)
            egfr = round(random.uniform(88.0, 115.0), 1)
            usg = round(random.uniform(1.012, 1.020), 3)
            protein = "NIL"

        rows.append([
            f"CLN-TEST-{1000 + i}",
            worker_id,
            (datetime(2025, 4, 15) + timedelta(days=i * 2)).strftime("%Y-%m-%d"),
            random.choice(facilities),
            "GMC-KUTCH-MD-4081",
            fev1, fvc, ratio, fev1_pct,
            ilo, opacities, creat, egfr,
            usg, protein,
            random.randint(95, 99),
            random.randint(68, 88),
            random.randint(118, 148),
            random.randint(76, 92),
            round(random.uniform(15.0, 45.0), 1),
            "NEGATIVE",
            verdict, cert
        ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 5. statutory_fitness_forms.csv
# ------------------------------------------------------------------------------
def generate_statutory_fitness_forms():
    file_path = TABLES_DIR / "statutory_fitness_forms.csv"
    headers = [
        "form_id", "worker_id", "form_type", "employer_id", "legal_exam_trigger_age",
        "certifying_surgeon_name", "issue_date", "renewal_due_date", "compliance_status"
    ]
    rows = []
    for i, worker_id in enumerate(WORKER_IDS):
        is_port = (i % 2 == 0)
        form_type = "CENTRAL_FORM_VIII" if is_port else "GUJARAT_FORM_5"
        trigger_age = 40 if is_port else 45
        issue = datetime(2025, 3, 1) + timedelta(days=i * 3)
        due = issue + timedelta(days=365)
        status = "COMPLIANT" if due > datetime(2025, 11, 1) else "OVERDUE_EXAM"

        rows.append([
            f"GOV-CERT-{2025000 + i}",
            worker_id,
            form_type,
            f"EMP-KCH-{random.randint(10, 25)}",
            trigger_age,
            "Dr. Rajesh V. Dave, Certifying Surgeon DISH Kutch",
            issue.strftime("%Y-%m-%d"),
            due.strftime("%Y-%m-%d"),
            status
        ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 6. health_facilities_kachchh.csv
# ------------------------------------------------------------------------------
def generate_health_facilities():
    file_path = TABLES_DIR / "health_facilities_kachchh.csv"
    headers = [
        "facility_id", "facility_name", "facility_tier", "taluka", "latitude", "longitude",
        "has_digital_xray", "has_spirometer", "has_audiometry", "has_biochemical_lab",
        "has_cbnaat_tb_testing", "emergency_108_base"
    ]
    facilities = [
        ["FAC-BHUJ-GK", "GK General Hospital (Govt Medical College)", "DISTRICT_HOSPITAL", "Bhuj", 23.2504, 69.6644, True, True, True, True, True, True],
        ["FAC-GANDHI-ESIC", "ESIC Model Hospital Gandhidham", "ESIC", "Gandhidham", 23.0753, 70.1337, True, True, True, True, True, True],
        ["FAC-MUNDRA-CHC", "Mundra Community Health Centre", "CHC", "Mundra", 22.8415, 69.7214, True, True, False, True, False, True],
        ["FAC-ANJAR-SDH", "Anjar Sub-District Hospital", "SUB_DISTRICT_HOSPITAL", "Anjar", 23.1165, 70.0287, True, True, False, True, True, True],
        ["FAC-MANDVI-CHC", "Mandvi Referal Hospital & CHC", "CHC", "Mandvi", 22.8328, 69.3558, True, True, False, True, False, True],
        ["FAC-ABDASA-CHC", "Naliya CHC (Abdasa)", "CHC", "Abdasa", 23.2580, 68.8315, True, False, False, True, False, True],
        ["FAC-NAKH-CHC", "Nakhatrana Community Health Centre", "CHC", "Nakhatrana", 23.3512, 69.2625, True, True, False, True, False, True],
        ["FAC-RAPAR-CHC", "Rapar Community Health Centre", "CHC", "Rapar", 23.5714, 70.6385, True, False, False, True, False, True],
        ["FAC-LAKH-PHC", "Dayapar Primary Health Centre (Lakhpat)", "PHC", "Lakhpat", 23.6821, 68.8812, False, False, False, True, False, True],
        ["FAC-BHACHAU-CHC", "Bhachau Community Health Centre", "CHC", "Bhachau", 23.2842, 70.3541, True, True, False, True, False, True],
        ["FAC-MOB-VAN-01", "BOCW Dhanvantari Arogya Rath #1 (Mundra/Kandla)", "MOBILE_VAN", "Mundra", 22.8395, 69.7258, True, True, True, True, False, True],
        ["FAC-MOB-VAN-02", "BOCW Dhanvantari Arogya Rath #2 (Little Rann Salt)", "MOBILE_VAN", "Rapar", 23.3500, 71.0500, True, True, False, True, False, True]
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(facilities)
    print(f"Generated: {file_path} ({len(facilities)} records)")

# ------------------------------------------------------------------------------
# 7. unregistered_worker_enrollment.csv
# ------------------------------------------------------------------------------
def generate_unregistered_enrollments():
    file_path = SIM_DIR / "unregistered_worker_enrollment.csv"
    headers = [
        "enrollment_id", "provisional_worker_id", "intake_channel", "enrollment_date",
        "eshram_uan_masked", "aadhaar_virtual_token", "contractor_declared",
        "prior_work_years_silica", "assigned_permanent_id"
    ]
    rows = []
    contractors = ["Kachchh Salt Works Labor Contractor", "Jay Ambe Construction Logistics", "Adani SEZ Sub-contractor", "Shree Ram Stone Quarry Labor Supply", "Self / Unorganized Agariya"]
    
    for i in range(1, 31):
        uan_tail = f"{random.randint(1000, 9999)}"
        rows.append([
            f"ENR-2025-{100 + i}",
            f"PROV-KCH-{500 + i}",
            random.choice(["MOBILE_HEALTH_VAN", "CLINIC_WALK_IN", "SITE_CAMP"]),
            (datetime(2025, 4, 1) + timedelta(days=i * 3)).strftime("%Y-%m-%d"),
            f"9842-XXXX-{uan_tail}",
            f"VID-TOKEN-{uuid.uuid4().hex[:12].upper()}",
            random.choice(contractors),
            round(random.uniform(2.0, 18.0), 1),
            f"W-KCH-{1000 + i}"
        ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 8. worker_consent_audit_log.csv
# ------------------------------------------------------------------------------
def generate_consent_audit_log():
    file_path = SIM_DIR / "worker_consent_audit_log.csv"
    headers = [
        "consent_event_id", "worker_id", "requester_role", "requester_id",
        "data_scope", "consent_method", "consent_status", "event_timestamp"
    ]
    rows = []
    roles = [
        ("CLINIC_STAFF", "DOC-4081", "FULL_CLINICAL", "OTP_VERIFIED"),
        ("DDO_ADMIN", "DDO-KUTCH-01", "ANONYMOUS_AGGREGATE", "STATUTORY_EMERGENCY"),
        ("SUPERVISOR", "SUP-MUNDRA-02", "RISK_FLAG_ONLY", "BIOMETRIC_TAP"),
        ("WORKER_SELF", "SELF", "FULL_CLINICAL", "OTP_VERIFIED")
    ]
    
    for i in range(1, 61):
        worker_id = random.choice(WORKER_IDS)
        r_role, r_id, scope, method = random.choice(roles)
        status = "GRANTED" if random.random() > 0.05 else "DENIED"
        ts = (datetime(2025, 5, 1) + timedelta(hours=i * 4)).isoformat()
        
        rows.append([
            f"CSNT-AUDIT-{2000 + i}",
            worker_id, r_role, r_id, scope, method, status, ts
        ])

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated: {file_path} ({len(rows)} records)")

# ------------------------------------------------------------------------------
# 9. local_silica_lab_assays.csv
# ------------------------------------------------------------------------------
def generate_silica_lab_assays():
    file_path = TABLES_DIR / "local_silica_lab_assays.csv"
    headers = [
        "assay_id", "location_id", "industry_type", "sample_collection_method",
        "respirable_dust_conc_mg_m3", "quartz_silica_pct_xrd", "cristobalite_pct_xrd",
        "testing_laboratory", "analysis_date"
    ]
    assays = [
        ["ASSAY-KCH-01", "abdasa_cement", "STONE_CRUSHING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 2.85, 18.4, 0.4, "NIOH Ahmedabad XRD Lab", "2025-02-14"],
        ["ASSAY-KCH-02", "abdasa_cement", "CEMENT_GRINDING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 1.94, 12.2, 0.2, "NIOH Ahmedabad XRD Lab", "2025-02-14"],
        ["ASSAY-KCH-03", "bhuj_hq", "QUARRY_DRILLING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 3.42, 22.8, 0.6, "NABL Accredited Envirocare Lab", "2025-03-01"],
        ["ASSAY-KCH-04", "anjar_steel", "BENTONITE_PROCESSING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 1.45, 8.5, 0.1, "NIOH Ahmedabad XRD Lab", "2025-03-10"],
        ["ASSAY-KCH-05", "kandla_dock", "BULK_MINERAL_HANDLING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 1.20, 6.2, 0.1, "Kandla Port Trust Environmental Lab", "2025-03-22"],
        ["ASSAY-KCH-06", "little_rann_salt", "SALT_PAN_RAKING", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 0.85, 3.1, 0.0, "NIOH Ahmedabad XRD Lab", "2025-04-05"],
        ["ASSAY-KCH-07", "mundra_port", "CONTAINER_YARD_DUST", "CYCLONE_RESPIRABLE_DUST_NIOSH_0600", 0.62, 4.5, 0.1, "Adani Environment Monitoring Center", "2025-04-12"]
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(assays)
    print(f"Generated: {file_path} ({len(assays)} records)")


if __name__ == "__main__":
    generate_bme280_telemetry()
    generate_rfid_qr_logs()
    generate_calibration_curves()
    generate_clinical_records()
    generate_statutory_fitness_forms()
    generate_health_facilities()
    generate_unregistered_enrollments()
    generate_consent_audit_log()
    generate_silica_lab_assays()
    print("ALL 9 MISSING DATASETS GENERATED SUCCESSFULLY!")
