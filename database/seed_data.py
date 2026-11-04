"""
================================================================================
KACHCHH OCCUPATIONAL HEALTH DATABASE SEEDER (PS000109)
================================================================================
Generates 1,000 realistic workers across 50 industrial sites in Kachchh district,
populating all 10 tables with longitudinal exposure, symptoms, and cases.
================================================================================
"""

import sqlite3
import random
import uuid
import hashlib
import sys
import os
from datetime import datetime, date, timedelta

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rules_engine.wbgt_calculator import WBGTCalculator, SensorCorrection


def seed_database(db_path: str = r"c:\Users\jaypa\OneDrive\Documents\SSIP\database\occupational_health.db"):
    random.seed(42) # Deterministic for reproducible pitch numbers
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    print("[1/8] Seeding 50 Industrial Sites in Kachchh...")
    talukas = [
        ("Mundra", 22.8390, 69.7120),
        ("Gandhidham", 23.0753, 70.1337),
        ("Anjar", 23.1130, 70.0270),
        ("Bhuj", 23.2420, 69.6669),
        ("Mandvi", 22.8280, 69.3550)
    ]
    site_types = ["salt_pan", "stone_crusher", "cement_plant", "port_berth"]
    
    sites_data = []
    site_ids = []
    
    for i in range(1, 51):
        s_id = str(uuid.uuid4())
        site_ids.append(s_id)
        taluka_name, base_lat, base_lon = random.choice(talukas)
        stype = random.choice(site_types)
        
        # Salt pans are mostly in Mundra, Gandhidham, and Mandvi coastal zones
        if i <= 25:
            stype = "salt_pan"
            taluka_name, base_lat, base_lon = random.choice([
                ("Mundra", 22.8390, 69.7120),
                ("Gandhidham", 23.0753, 70.1337),
                ("Mandvi", 22.8280, 69.3550)
            ])
        elif i <= 38:
            stype = "stone_crusher"
            taluka_name, base_lat, base_lon = random.choice([
                ("Anjar", 23.1130, 70.0270),
                ("Bhuj", 23.2420, 69.6669)
            ])
            
        lat = base_lat + random.uniform(-0.08, 0.08)
        lon = base_lon + random.uniform(-0.08, 0.08)
        
        # Realistic infrastructure distribution (IDR / TISS findings: many salt pans lack water/toilets)
        has_water = random.random() > 0.40 if stype == "salt_pan" else random.random() > 0.15
        has_toilet = random.random() > 0.65 if stype == "salt_pan" else random.random() > 0.25
        has_shade = random.random() > 0.50
        
        sname = f"{taluka_name} {stype.replace('_', ' ').title()} Unit {i:02d}"
        
        sites_data.append((
            s_id, sname, stype, taluka_name, "Kachchh",
            round(lat, 6), round(lon, 6),
            1 if has_water else 0,
            1 if has_toilet else 0,
            1 if has_shade else 0,
            random.randint(20, 150),
            f"Supervisor {chr(65 + (i % 26))}. Patel",
            f"+91 9825{random.randint(100000, 999999)}"
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO sites (
            site_id, site_name, site_type, taluka, district, latitude, longitude,
            has_potable_water, has_toilets, has_shaded_rest_area, active_worker_capacity,
            supervisor_name, supervisor_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sites_data)

    print("[2/8] Seeding 1,000 Workers with e-Shram UAN and ABHA Records...")
    first_names = ["Ramesh", "Kishore", "Dinesh", "Bharat", "Haresh", "Pravin", "Suresh", "Mahesh", "Devji", "Kalu", "Jiva", "Gopal", "Laxman", "Geeta", "Kamla", "Shanta", "Leela", "Manju", "Kanku"]
    last_names = ["Ahir", "Rabari", "Koli", "Vankar", "Gadhvi", "Marwada", "Maheshwari", "Chauhan", "Jadeja", "Patel"]
    
    workers_data = []
    worker_ids = []
    
    for i in range(1, 1001):
        w_id = str(uuid.uuid4())
        worker_ids.append(w_id)
        
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        gender = "Female" if fname in ["Geeta", "Kamla", "Shanta", "Leela", "Manju", "Kanku"] else "Male"
        age = random.randint(19, 58)
        
        # Assigned site
        assigned_site = random.choice(site_ids)
        # Job role matched to site type
        site_type = [s[2] for s in sites_data if s[0] == assigned_site][0]
        if site_type == "salt_pan":
            role = "salt_raker" if gender == "Male" else "salt_gatherer"
        elif site_type == "stone_crusher":
            role = random.choice(["crusher_operator", "rock_driller", "sorter"])
        elif site_type == "cement_plant":
            role = random.choice(["cement_loader", "bagging_operator", "mill_operator"])
        else: # port_berth
            role = random.choice(["truck_driver", "bulk_cargo_loader", "crane_operator"])
            
        # 12-digit e-Shram UAN
        eshram = f"1000{i:08d}"
        abha_id = f"91-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{i:04d}"
        abha_addr = f"{fname.lower()}.{lname.lower()}{i}@abdm"
        qr_hash = hashlib.sha256(f"{eshram}_{i}".encode()).hexdigest()
        
        # Privacy & Consent: 97% opt-in, 3% unconsented
        consent = 1 if random.random() < 0.97 else 0
        
        workers_data.append((
            w_id, eshram, abha_id, abha_addr, qr_hash,
            fname, lname, gender, age, assigned_site, role,
            f"+91 9712{random.randint(100000, 999999)}",
            "gu" if random.random() < 0.85 else "hi",
            consent,
            round(random.uniform(2.2, 4.2), 2), # Baseline FEV1 (liters)
            round(random.uniform(0.7, 1.1), 2), # Baseline Creatinine (mg/dL)
            1
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO workers (
            worker_id, eshram_uan, abha_id, abha_address, qr_card_hash,
            first_name, last_name, gender, age, current_site_id, job_role,
            phone_number, preferred_language, consent_given,
            baseline_fev1_liters, baseline_serum_creatinine, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, workers_data)

    print("[3/8] Seeding Ambient Devices & Personal Badges...")
    devices_data = []
    
    # 50 Site Nodes
    for i, s_id in enumerate(site_ids, 1):
        dev_id = f"SITE-NODE-{i:03d}"
        mac = f"24:6F:28:{i:02X}:AA:{random.randint(10, 99):02X}"
        devices_data.append((
            dev_id, "site_node", mac, "v1.2_150mm_Globe", "fw_2.4.1",
            s_id, None, "ACTIVE", random.randint(85, 100)
        ))
        
    # 100 Personal Dust Badges
    for i in range(1, 101):
        dev_id = f"DUST-BADGE-{i:03d}"
        mac = f"30:AE:A4:{i:02X}:BB:{random.randint(10, 99):02X}"
        devices_data.append((
            dev_id, "personal_dust_badge", mac, "v1.0_PMS5003_INMP441", "fw_1.8.0",
            workers_data[i-1][9], # worker's site
            worker_ids[i-1],      # worker_id
            "ACTIVE", random.randint(70, 100)
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO devices (
            device_id, device_type, mac_address, hardware_version, firmware_version,
            assigned_site_id, assigned_worker_id, status, battery_level_pct
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, devices_data)

    print("[4/8] Seeding Rules Table...")
    rules_data = [
        ("RULE_WBGT_RED_31C", "ISO 7243 Stop Work / Emergency Heat Stress", "HEAT", ">=", 31.0, 1, "LAMP_COLOR", '{"lamp": "RED", "work_pct": 25, "sound_alert": true}', 1, "Mandatory work cessation or 15m work/45m rest schedule."),
        ("RULE_WBGT_ORANGE_29C", "ISO 7243 Danger Heat Stress", "HEAT", ">=", 29.5, 1, "LAMP_COLOR", '{"lamp": "ORANGE", "work_pct": 50}', 1, "Enforce 30 min work / 30 min rest; ORS hydration."),
        ("RULE_WBGT_YELLOW_28C", "ISO 7243 Warning Heat Stress", "HEAT", ">=", 28.0, 1, "LAMP_COLOR", '{"lamp": "YELLOW", "work_pct": 75}', 1, "Enforce 45 min work / 15 min shaded rest."),
        ("RULE_SILICA_CUMULATIVE_DOSE", "30-Day Cumulative Respirable Silica Dose", "SILICA_DUST", ">=", 2.5, 30, "SCHEDULE_VAN", '{"facility": "Gujarat BOCW Dhanvantari Rath", "tests": ["spirometry", "xray"]}', 1, "Triggers mobile van spirometry and chest X-ray screening under Factories Act 41C."),
        ("RULE_HEAT_KIDNEY_ACUTE", "Repeated Heat Strain & Dehydration (CKDu)", "DEHYDRATION", ">=", 2.0, 7, "SCHEDULE_VAN", '{"facility": "Salt-Worker Medical Van", "tests": ["serum_creatinine", "urine_analysis"]}', 1, "Triggers kidney function screening for salt pan nephropathy prevention.")
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO rules (
            rule_id, rule_name, hazard_type, operator, threshold_value,
            window_days, action_type, target_payload, is_active, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rules_data)

    print("[5/8] Seeding Longitudinal Daily Exposure (Past 30 Days for 1,000 Workers)...")
    daily_exposure_data = []
    cases_data = []
    symptoms_data = []
    alerts_data = []
    
    today = date.today()
    
    for w_idx, w in enumerate(workers_data):
        w_id = w[0]
        s_id = w[9]
        job_role = w[10]
        site_type = [s[2] for s in sites_data if s[0] == s_id][0]
        
        cumulative_dust = 0.0
        dark_urine_count = 0
        
        for day_offset in range(30, -1, -1):
            s_date = today - timedelta(days=day_offset)
            
            # Weather pattern simulation based on real Kachchh seasonal variations
            # Salt pans and coastal zones have high WBGT and high humidity
            base_temp = 34.0 + random.uniform(-4.0, 8.0)
            base_rh = 68.0 + random.uniform(-15.0, 22.0)
            
            # Estimate WBGT
            wbgt_est = WBGTCalculator.estimate_wbgt_from_weather(base_temp, base_rh)
            wbgt_c = wbgt_est["wbgt_outdoor_c"]
            max_wbgt = round(wbgt_c + random.uniform(1.0, 3.5), 1)
            
            # Dust profile based on job role
            if job_role in ["crusher_operator", "rock_driller"]:
                avg_pm25 = random.uniform(90.0, 240.0)
                peak_pm25 = avg_pm25 + random.uniform(60.0, 180.0)
            elif job_role in ["cement_loader", "bagging_operator"]:
                avg_pm25 = random.uniform(70.0, 190.0)
                peak_pm25 = avg_pm25 + random.uniform(40.0, 120.0)
            elif job_role in ["salt_raker", "salt_gatherer"]:
                avg_pm25 = random.uniform(15.0, 45.0) # Lower dust, but extreme WBGT
                peak_pm25 = avg_pm25 + random.uniform(10.0, 30.0)
                max_wbgt = max(max_wbgt, 31.2 + random.uniform(-0.5, 2.0))
            else:
                avg_pm25 = random.uniform(30.0, 85.0)
                peak_pm25 = avg_pm25 + random.uniform(20.0, 60.0)
                
            shift_hours = 8.5
            dose = (avg_pm25 / 1000.0) * shift_hours
            cumulative_dust += dose
            
            # Calculate hours above WBGT 28C and 30C
            hrs_28 = max(0.0, round((max_wbgt - 27.5) * 1.5, 1)) if max_wbgt >= 28.0 else 0.0
            hrs_30 = max(0.0, round((max_wbgt - 29.5) * 1.8, 1)) if max_wbgt >= 30.0 else 0.0
            hrs_28 = min(hrs_28, shift_hours)
            hrs_30 = min(hrs_30, shift_hours)
            
            # Determine over-exposure flag
            flag = False
            reasons = []
            
            if cumulative_dust > 2.5:
                flag = True
                reasons.append("Cumulative dust threshold exceeded (>2.5 mg/m³·hr)")
            if hrs_30 >= 4.0:
                flag = True
                reasons.append(f"Excessive severe heat strain ({hrs_30} hrs > 30°C WBGT)")
                
            daily_exposure_data.append((
                w_id, s_id, s_date, shift_hours,
                round(avg_pm25, 1), round(peak_pm25, 1), round(avg_pm25 * 2.1, 1),
                round(cumulative_dust, 3),
                round(wbgt_c, 1), max_wbgt, hrs_28, hrs_30,
                random.randint(1, 4),
                round(random.uniform(2.0, 4.5), 1),
                1 if flag else 0,
                "; ".join(reasons) if reasons else None
            ))
            
            # Seed Symptoms for recent days
            if day_offset <= 7:
                has_dark_urine = 1 if (hrs_30 > 2.5 and random.random() < 0.45) else 0
                has_dizziness = 1 if (hrs_30 > 3.0 and random.random() < 0.35) else 0
                has_cough = 1 if (job_role in ["crusher_operator", "cement_loader"] and random.random() < 0.40) else 0
                has_glare = 1 if (site_type == "salt_pan" and random.random() < 0.50) else 0
                has_skin = 1 if (site_type == "salt_pan" and random.random() < 0.30) else 0
                
                if has_dark_urine:
                    dark_urine_count += 1
                    
                if any([has_dark_urine, has_dizziness, has_cough, has_glare, has_skin]):
                    symptoms_data.append((
                        w_id, s_date,
                        has_dark_urine, has_dizziness,
                        1 if random.random() < 0.4 else 0, # thirst
                        1 if random.random() < 0.25 else 0, # cramps
                        has_cough,
                        1 if has_cough and random.random() < 0.5 else 0, # dyspnea
                        1 if has_cough and random.random() < 0.3 else 0, # tightness
                        has_glare, has_skin,
                        1 if job_role == "truck_driver" and random.random() < 0.4 else 0,
                        "SUPERVISOR",
                        sum([has_dark_urine*3, has_dizziness*2, has_cough*2, has_glare, has_skin])
                    ))
                    
        # Trigger Clinical Screening Cases based on real risk criteria
        if cumulative_dust > 2.5 and job_role in ["crusher_operator", "rock_driller", "cement_loader"]:
            cases_data.append((
                str(uuid.uuid4()), w_id, s_id, "DUST_SILICOSIS_SUSPECT",
                "RULE_SILICA_CUMULATIVE_DOSE",
                random.choice(["PENDING_SCREENING", "VAN_SCHEDULED", "SCREENED"]),
                random.randint(4, 5),
                "Gujarat BOCW Dhanvantari Rath",
                today + timedelta(days=random.randint(1, 10)),
                today - timedelta(days=2) if random.random() < 0.3 else None,
                round(random.uniform(0.65, 0.85), 2),
                random.choice(["0/0", "1/0", "1/1"]),
                round(random.uniform(0.8, 1.2), 2),
                1.020,
                "Referred due to high 30-day cumulative respirable silica exposure.",
                "GMC-KUTCH-MD-4081",
                0
            ))
        elif dark_urine_count >= 2 and site_type == "salt_pan":
            cases_data.append((
                str(uuid.uuid4()), w_id, s_id, "HEAT_NEPHROPATHY_SUSPECT",
                "RULE_HEAT_KIDNEY_ACUTE",
                random.choice(["PENDING_SCREENING", "VAN_SCHEDULED"]),
                5,
                "Salt-Worker Medical Van",
                today + timedelta(days=random.randint(1, 5)),
                None,
                round(random.uniform(0.75, 0.90), 2),
                "0/0",
                round(random.uniform(1.2, 1.8), 2), # Elevated creatinine
                1.028, # High specific gravity (dehydration)
                "Clinical referral: recurrent dark urine following severe heat index (>30C WBGT). Serum creatinine check required.",
                "GMC-BHUJ-PHYS-1029",
                0
            ))

    cur.executemany("""
        INSERT OR REPLACE INTO daily_exposure (
            worker_id, site_id, shift_date, shift_duration_hours,
            avg_pm2_5_ug_m3, peak_pm2_5_ug_m3, avg_pm10_ug_m3,
            cumulative_dust_dose_mg_m3_hr, avg_wbgt_c, max_wbgt_c,
            hours_above_wbgt_28, hours_above_wbgt_30,
            rest_breaks_taken, water_intake_logged_liters,
            flag_over_exposure, flag_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, daily_exposure_data)

    cur.executemany("""
        INSERT INTO symptoms (
            worker_id, shift_date,
            dark_urine, dizziness_or_fainting, extreme_thirst, muscle_cramps,
            persistent_cough, shortness_of_breath, chest_tightness,
            eye_burning_salt_glare, skin_lesions_brine_burns,
            back_pain_whole_body_vibration, logged_by, severity_rank
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, symptoms_data)

    cur.executemany("""
        INSERT OR REPLACE INTO cases (
            case_id, worker_id, site_id, case_type, trigger_rule_id,
            status, priority_score, assigned_facility, scheduled_screening_date,
            screened_date, spirometry_fev1_fvc_ratio, chest_xray_ilo_category,
            serum_creatinine_mg_dl, urine_specific_gravity, clinical_notes,
            doctor_registration_no, bocw_assistance_claimed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cases_data)

    print("[6/8] Seeding Recent High-Frequency Readings (Last 4 Hours)...")
    readings_data = []
    now = datetime.now()
    
    for s in sites_data:
        s_id = s[0]
        dev_id = f"SITE-NODE-{site_ids.index(s_id)+1:03d}"
        for offset_min in range(0, 240, 15):
            t = now - timedelta(minutes=offset_min)
            temp = round(34.5 + random.uniform(-2.5, 4.0), 1)
            rh = round(72.0 + random.uniform(-10.0, 15.0), 1)
            wbgt_info = WBGTCalculator.estimate_wbgt_from_weather(temp, rh)
            
            readings_data.append((
                dev_id, None, s_id, t.strftime("%Y-%m-%d %H:%M:%S"),
                round(random.uniform(15.0, 40.0), 1),
                round(random.uniform(30.0, 85.0), 1),
                round(random.uniform(70.0, 160.0), 1),
                temp, rh,
                wbgt_info["estimated_globe_temp_c"],
                wbgt_info["estimated_wet_bulb_c"],
                wbgt_info["wbgt_outdoor_c"],
                round(random.uniform(6.0, 11.5), 1),
                round(random.uniform(55.0, 85.0), 1),
                0.02,
                0
            ))

    cur.executemany("""
        INSERT INTO readings (
            device_id, worker_id, site_id, recorded_at,
            pm1_0_ug_m3, pm2_5_ug_m3, pm10_0_ug_m3,
            ambient_temp_c, relative_humidity_pct, globe_temp_c,
            natural_wet_bulb_c, calculated_wbgt_c,
            uv_index, noise_dba, vibration_rms_g, is_offline_buffered
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, readings_data)

    print("[7/8] Seeding Dispatched Alerts...")
    alerts_data = [
        (str(uuid.uuid4()), site_ids[0], "SITE-NODE-001", None, "CRITICAL", "HEAT",
         "CRITICAL HEAT STRESS (WBGT 31.4°C): Mandatory stop of heavy salt raking. 45m shaded rest enforced.",
         "ચેતવણી: અતિશય ગરમી (WBGT 31.4°C)! મીઠાના અગરમાં કામ અટકાવો. ૪૫ મિનિટ છાંયડામાં આરામ ફરજિયાત.",
         "अत्यधिक गर्मी चेतावनी (WBGT 31.4°C)! काम रोकें। 45 मिनट छाया में आराम अनिवार्य है।",
         "RED", "+91 9825123456", 1, 1, "Supervisor A. Patel", "2026-11-04 13:45:00"),
        (str(uuid.uuid4()), site_ids[26], "SITE-NODE-027", None, "WARNING", "DUST",
         "HAZARDOUS DUST SPIKE (PM2.5: 285 µg/m³): Crusher area water spray active; N95 masks mandatory.",
         "ધૂળનું જોખમી સ્તર (PM2.5: 285 µg/m³)! ક્રશર વિસ્તારમાં પાણીનો છંટકાવ ચાલુ કરો અને માસ્ક પહેરો.",
         "धूल का खतरनाक स्तर (PM2.5: 285 µg/m³)! पानी का छिड़काव करें और मास्क पहनना जरूरी है।",
         "ORANGE", "+91 9825654321", 0, 1, "Supervisor B. Ahir", "2026-11-04 11:20:00")
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO alerts (
            alert_id, site_id, device_id, worker_id, alert_severity, hazard_type,
            message_en, message_gu, message_hi, lamp_color_command,
            sms_sent_to, ivr_call_dispatched, is_acknowledged, acknowledged_by, acknowledged_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts_data)

    print("[8/8] Seeding Export Audit Logs...")
    exports_data = [
        (str(uuid.uuid4()), "BOCW_VAN_DUE_LIST", "Gujarat BOCW Welfare Board", 42, "CSV",
         "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "exports/bocw_van_due_20261104.csv"),
        (str(uuid.uuid4()), "SALT_PAN_PRIORITY_LIST", "Industries Commissionerate", 28, "CSV",
         "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", 0, "exports/salt_van_due_20261104.csv"),
        (str(uuid.uuid4()), "NPCCHH_DISTRICT_HEAT_REPORT", "DDO Kachchh", 50, "JSON",
         "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a", 1, "exports/npcchh_heat_weekly_2026w44.json")
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO exports (
            export_id, export_type, target_agency, record_count, format,
            checksum_sha256, is_anonymized, file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, exports_data)

    con.commit()
    con.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
