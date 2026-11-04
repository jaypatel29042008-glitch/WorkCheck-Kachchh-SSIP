-- ============================================================================
-- DUST-HEAT OCCUPATIONAL HEALTH MONITORING SYSTEM (PS000109)
-- PRODUCTION DATABASE DDL (PostgreSQL 15+ / SQLite 3 Compatible ANSI SQL)
-- ============================================================================
-- Architecture:
-- 1. Tiered Storage: High-frequency telemetry (readings) -> Daily rollup (daily_exposure)
-- 2. Privacy-by-Design: DPDP Act 2023 compliance, consent audits, anonymous district views
-- 3. Interoperability: ABDM/ABHA integration, e-Shram 12-digit UAN, BOCW/ESIC export schemas
-- ============================================================================

-- Drop views if existing
DROP VIEW IF EXISTS district_anonymous_risk_summary;
DROP VIEW IF EXISTS district_taluka_heat_summary;
DROP VIEW IF EXISTS workers_due_for_screening_view;

-- Drop tables if existing (in reverse dependency order)
DROP TABLE IF EXISTS exports;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS cases;
DROP TABLE IF EXISTS rules;
DROP TABLE IF EXISTS daily_exposure;
DROP TABLE IF EXISTS readings;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS workers;
DROP TABLE IF EXISTS sites;

-- ----------------------------------------------------------------------------
-- 1. SITES TABLE
-- Physical work environments (Salt pans in Little Rann / coastal Mundra,
-- stone crushing units, cement plants, port berths).
-- ----------------------------------------------------------------------------
CREATE TABLE sites (
    site_id VARCHAR(36) PRIMARY KEY,                    -- UUID v4
    site_name VARCHAR(120) NOT NULL,                    -- e.g., 'Mundra Salt Pan Unit 4B'
    site_type VARCHAR(40) NOT NULL,                     -- 'salt_pan', 'stone_crusher', 'cement_plant', 'port_berth'
    taluka VARCHAR(50) NOT NULL,                        -- 'Mundra', 'Anjar', 'Bhuj', 'Gandhidham', 'Mandvi'
    district VARCHAR(50) NOT NULL DEFAULT 'Kachchh',
    latitude DECIMAL(9, 6) NOT NULL,                    -- e.g., 22.839000
    longitude DECIMAL(9, 6) NOT NULL,                   -- e.g., 69.712000
    has_potable_water BOOLEAN NOT NULL DEFAULT FALSE,   -- Critical dehydration mitigation check
    has_toilets BOOLEAN NOT NULL DEFAULT FALSE,         -- Key factor in sanitation & hydration compliance
    has_shaded_rest_area BOOLEAN NOT NULL DEFAULT FALSE,-- Mandatory under OSH Code 2020
    active_worker_capacity INT NOT NULL DEFAULT 50,
    supervisor_name VARCHAR(100),
    supervisor_phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. WORKERS TABLE
-- Identity, consent, and demographic data.
-- Uses 12-digit e-Shram UAN as national identifier & ABHA address for ABDM health records.
-- ----------------------------------------------------------------------------
CREATE TABLE workers (
    worker_id VARCHAR(36) PRIMARY KEY,                  -- UUID v4
    eshram_uan CHAR(12) UNIQUE,                         -- 12-digit e-Shram Universal Account Number
    abha_id VARCHAR(50),                                -- Ayushman Bharat Health Account (e.g. 12-3456-7890-1234)
    abha_address VARCHAR(100),                          -- e.g. 'worker.kutch@abdm'
    qr_card_hash VARCHAR(64) NOT NULL UNIQUE,          -- SHA-256 hash printed on worker's QR badge
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    gender VARCHAR(10) NOT NULL,                        -- 'Male', 'Female', 'Other'
    age INT NOT NULL,
    current_site_id VARCHAR(36) REFERENCES sites(site_id),
    job_role VARCHAR(50) NOT NULL,                      -- 'salt_raker', 'crusher_operator', 'cement_loader', 'truck_driver'
    phone_number VARCHAR(15),                           -- For direct SMS / IVR voice alerts
    preferred_language VARCHAR(10) DEFAULT 'gu',        -- 'gu' (Gujarati), 'hi' (Hindi), 'en' (English)
    
    -- Privacy & Consent (DPDP Act 2023 Compliance)
    consent_given BOOLEAN NOT NULL DEFAULT TRUE,        -- Opt-in for exposure telemetry & van booking
    consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consent_version VARCHAR(20) DEFAULT 'v1.0_2026',
    consent_revoked_at TIMESTAMP,                       -- If set, telemetry cannot link to worker identity
    
    -- Health Baseline
    baseline_fev1_liters DECIMAL(4, 2),                -- Baseline Forced Expiratory Volume (Spirometry)
    baseline_serum_creatinine DECIMAL(4, 2),            -- Kidney marker (mg/dL)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. DEVICES TABLE
-- Hardware nodes: Ambient Site Nodes (WBGT + PM10 + UV) and Personal Badges.
-- ----------------------------------------------------------------------------
CREATE TABLE devices (
    device_id VARCHAR(36) PRIMARY KEY,                  -- UUID v4 / Hardware EUI
    device_type VARCHAR(30) NOT NULL,                   -- 'site_node', 'personal_dust_badge', 'vibration_logger'
    mac_address VARCHAR(17) UNIQUE NOT NULL,            -- e.g., '24:6F:28:XX:YY:ZZ'
    hardware_version VARCHAR(20) NOT NULL,             -- e.g., 'v1.2_150mm_Globe'
    firmware_version VARCHAR(20) NOT NULL,             -- e.g., 'fw_2.4.1_mesh'
    assigned_site_id VARCHAR(36) REFERENCES sites(site_id),
    assigned_worker_id VARCHAR(36) REFERENCES workers(worker_id), -- Populated only for personal dust badges
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',       -- 'ACTIVE', 'OFFLINE', 'CALIBRATING', 'DECOMMISSIONED'
    battery_level_pct INT DEFAULT 100,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 4. READINGS TABLE (High-Frequency Raw Sensor Telemetry)
-- Generated every 10 seconds to 5 minutes by Site Nodes and Badges.
-- RETENTION POLICY: Kept raw for 30 days (up to 90 days in cold storage).
-- Summarized nightly into DAILY_EXPOSURE, then purged/archived to control disk growth.
-- ----------------------------------------------------------------------------
CREATE TABLE readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,       -- In PostgreSQL: BIGSERIAL
    device_id VARCHAR(36) NOT NULL REFERENCES devices(device_id),
    worker_id VARCHAR(36) REFERENCES workers(worker_id),-- NULL for static site node readings
    site_id VARCHAR(36) NOT NULL REFERENCES sites(site_id),
    recorded_at TIMESTAMP NOT NULL,
    
    -- Particulate Matter (PMS5003 / Alphasense with humidity correction)
    pm1_0_ug_m3 DECIMAL(6, 2),                         -- PM 1.0 (ug/m3)
    pm2_5_ug_m3 DECIMAL(6, 2),                         -- PM 2.5 (ug/m3)
    pm10_0_ug_m3 DECIMAL(6, 2),                        -- PM 10.0 (ug/m3)
    
    -- Thermal & Environmental Parameters (ISO 7243 WBGT Calculation)
    ambient_temp_c DECIMAL(4, 2) NOT NULL,             -- Dry Bulb Temp (Ta)
    relative_humidity_pct DECIMAL(4, 1) NOT NULL,      -- Relative Humidity (RH)
    globe_temp_c DECIMAL(4, 2),                        -- 150mm Matte-Black Globe Temp (Tg)
    natural_wet_bulb_c DECIMAL(4, 2),                  -- Natural Wet Bulb Temp (Tnw)
    calculated_wbgt_c DECIMAL(4, 2) NOT NULL,          -- 0.7*Tnw + 0.2*Tg + 0.1*Ta (Outdoor)
    
    -- Additional Environmental Hazards
    uv_index DECIMAL(4, 1),                            -- GUVA-S12SD UV Sensor on Site Node
    noise_dba DECIMAL(5, 1),                           -- INMP441 Microphone (Sound Pressure Level)
    vibration_rms_g DECIMAL(5, 3),                     -- MPU6050 Accelerometer (Heavy vehicle drivers)
    
    -- Transmission Metadata
    is_offline_buffered BOOLEAN DEFAULT FALSE,         -- True if replayed after network reconnection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_readings_worker_time ON readings(worker_id, recorded_at);
CREATE INDEX idx_readings_site_time ON readings(site_id, recorded_at);

-- ----------------------------------------------------------------------------
-- 5. DAILY_EXPOSURE TABLE (Permanent Summarized Rollup)
-- Nightly aggregate per worker per day.
-- RETENTION POLICY: PERMANENT (Used for longitudinal occupational disease tracking).
-- ----------------------------------------------------------------------------
CREATE TABLE daily_exposure (
    exposure_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- In PostgreSQL: BIGSERIAL
    worker_id VARCHAR(36) NOT NULL REFERENCES workers(worker_id),
    site_id VARCHAR(36) NOT NULL REFERENCES sites(site_id),
    shift_date DATE NOT NULL,
    shift_duration_hours DECIMAL(4, 2) NOT NULL DEFAULT 8.0,
    
    -- Dust Metrics
    avg_pm2_5_ug_m3 DECIMAL(6, 2),
    peak_pm2_5_ug_m3 DECIMAL(6, 2),
    avg_pm10_ug_m3 DECIMAL(6, 2),
    cumulative_dust_dose_mg_m3_hr DECIMAL(6, 3) NOT NULL, -- Cumulative dose (mg/m3 * hr)
    
    -- Heat Metrics (ISO 7243 Exceedances)
    avg_wbgt_c DECIMAL(4, 2) NOT NULL,
    max_wbgt_c DECIMAL(4, 2) NOT NULL,
    hours_above_wbgt_28 DECIMAL(4, 2) NOT NULL DEFAULT 0.0, -- Warning threshold for heavy labor
    hours_above_wbgt_30 DECIMAL(4, 2) NOT NULL DEFAULT 0.0, -- Action threshold (danger zone)
    
    -- Mitigation Log
    rest_breaks_taken INT DEFAULT 0,
    water_intake_logged_liters DECIMAL(4, 1),
    
    -- Decision Triggers
    flag_over_exposure BOOLEAN NOT NULL DEFAULT FALSE,
    flag_reason VARCHAR(150),                          -- e.g. 'Exceeded 30-day silica dose limit; 4 hrs > 30C WBGT'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(worker_id, shift_date)
);

CREATE INDEX idx_daily_exposure_lookup ON daily_exposure(worker_id, shift_date);

-- ----------------------------------------------------------------------------
-- 6. RULES TABLE
-- Dynamic Thresholds & Trigger Logic for the Rules Engine.
-- ----------------------------------------------------------------------------
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,                   -- e.g. 'RULE_WBGT_RED_30C'
    rule_name VARCHAR(100) NOT NULL,
    hazard_type VARCHAR(30) NOT NULL,                  -- 'HEAT', 'SILICA_DUST', 'DEHYDRATION', 'NOISE'
    operator VARCHAR(10) NOT NULL,                     -- '>', '>=', '<', '<=', 'EQUALS'
    threshold_value DECIMAL(8, 3) NOT NULL,
    window_days INT DEFAULT 1,                         -- Evaluation window (1 day, 7 days, 30 days)
    action_type VARCHAR(50) NOT NULL,                  -- 'LAMP_COLOR', 'SMS_ALERT', 'SCHEDULE_VAN', 'ESIC_REFERRAL'
    target_payload TEXT,                               -- JSON with specific parameters (e.g. lamp: 'RED', sound: true)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT
);

-- ----------------------------------------------------------------------------
-- 7. CASES TABLE (Occupational Health Management)
-- Tracks scheduled check-ups, Dhanvantari mobile van visits, and clinical referrals.
-- ----------------------------------------------------------------------------
CREATE TABLE cases (
    case_id VARCHAR(36) PRIMARY KEY,                    -- UUID v4
    worker_id VARCHAR(36) NOT NULL REFERENCES workers(worker_id),
    site_id VARCHAR(36) NOT NULL REFERENCES sites(site_id),
    case_type VARCHAR(40) NOT NULL,                     -- 'DUST_SILICOSIS_SUSPECT', 'HEAT_NEPHROPATHY_SUSPECT', 'ROUTINE_ANNUAL'
    trigger_rule_id VARCHAR(50) REFERENCES rules(rule_id),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING_SCREENING', -- 'PENDING_SCREENING', 'VAN_SCHEDULED', 'SCREENED', 'REFERRED_ESIC', 'CLOSED'
    priority_score INT NOT NULL DEFAULT 1,             -- 1 (Lowest) to 5 (Immediate Critical Priority)
    
    -- Delivery Channel / Scheme Mapping
    assigned_facility VARCHAR(80),                      -- 'Gujarat BOCW Dhanvantari Rath', 'Salt-Worker Medical Van', 'ESIC Dispensary Gandhidham'
    scheduled_screening_date DATE,
    screened_date DATE,
    
    -- Clinical Results
    spirometry_fev1_fvc_ratio DECIMAL(4, 2),           -- < 0.70 indicates obstructive defect
    chest_xray_ilo_category VARCHAR(10),               -- '0/-', '1/0', '1/1' (Silicosis grading)
    serum_creatinine_mg_dl DECIMAL(4, 2),              -- Elevated > 1.3 indicates acute kidney impairment
    urine_specific_gravity DECIMAL(5, 3),              -- > 1.025 indicates severe clinical dehydration
    clinical_notes TEXT,
    doctor_registration_no VARCHAR(50),
    
    -- Compensation & Welfare Linkage
    bocw_assistance_claimed BOOLEAN DEFAULT FALSE,     -- BOCW Assistance for Occupational Diseases
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 8. SYMPTOMS TABLE
-- Daily symptom reporting logged via Supervisor Tablet or Worker Self-Service QR Kiosk.
-- ----------------------------------------------------------------------------
CREATE TABLE symptoms (
    symptom_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- In PostgreSQL: BIGSERIAL
    worker_id VARCHAR(36) NOT NULL REFERENCES workers(worker_id),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shift_date DATE NOT NULL,
    
    -- Heat-Related Symptoms
    dark_urine BOOLEAN NOT NULL DEFAULT FALSE,         -- Cardinal indicator of dehydration
    dizziness_or_fainting BOOLEAN NOT NULL DEFAULT FALSE,
    extreme_thirst BOOLEAN NOT NULL DEFAULT FALSE,
    muscle_cramps BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Respiratory Symptoms
    persistent_cough BOOLEAN NOT NULL DEFAULT FALSE,
    shortness_of_breath BOOLEAN NOT NULL DEFAULT FALSE,
    chest_tightness BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Physical & Environmental Symptoms
    eye_burning_salt_glare BOOLEAN NOT NULL DEFAULT FALSE, -- Salt pan sun reflection
    skin_lesions_brine_burns BOOLEAN NOT NULL DEFAULT FALSE,-- Brine exposure on feet/hands
    back_pain_whole_body_vibration BOOLEAN NOT NULL DEFAULT FALSE,
    
    logged_by VARCHAR(30) NOT NULL DEFAULT 'SUPERVISOR',-- 'SUPERVISOR', 'WORKER_KIOSK', 'HEALTH_VAN'
    severity_rank INT NOT NULL DEFAULT 0               -- 0 to 10 computed severity score
);

-- ----------------------------------------------------------------------------
-- 9. ALERTS TABLE
-- Dispatched automated warnings (Colored Lamps, SMS, IVR Voice, Dashboard).
-- ----------------------------------------------------------------------------
CREATE TABLE alerts (
    alert_id VARCHAR(36) PRIMARY KEY,                  -- UUID v4
    site_id VARCHAR(36) NOT NULL REFERENCES sites(site_id),
    device_id VARCHAR(36) REFERENCES devices(device_id),
    worker_id VARCHAR(36) REFERENCES workers(worker_id),-- Optional: individual worker alert
    alert_severity VARCHAR(20) NOT NULL,               -- 'INFO', 'WARNING', 'CRITICAL', 'EMERGENCY'
    hazard_type VARCHAR(30) NOT NULL,                  -- 'HEAT', 'DUST', 'DEHYDRATION', 'FACILITY_MISSING'
    
    -- Multilingual Alert Delivery
    message_en TEXT NOT NULL,
    message_gu TEXT NOT NULL,                          -- Gujarati (Native local vernacular)
    message_hi TEXT NOT NULL,                          -- Hindi (Interstate migrant workers)
    
    -- Channels Dispatched
    lamp_color_command VARCHAR(10),                    -- 'GREEN', 'YELLOW', 'ORANGE', 'RED', 'FLASH_RED'
    sms_sent_to VARCHAR(15),
    ivr_call_dispatched BOOLEAN DEFAULT FALSE,
    
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 10. EXPORTS TABLE
-- Audit log of batch extracts for Government systems (BOCW, ESIC, NPCCHH).
-- ----------------------------------------------------------------------------
CREATE TABLE exports (
    export_id VARCHAR(36) PRIMARY KEY,                 -- UUID v4
    export_type VARCHAR(50) NOT NULL,                  -- 'BOCW_VAN_DUE_LIST', 'SALT_PAN_PRIORITY_LIST', 'ESIC_REFERRAL_BATCH', 'NPCCHH_DISTRICT_HEAT_REPORT'
    target_agency VARCHAR(80) NOT NULL,                -- 'Gujarat BOCW Welfare Board', 'Industries Commissionerate', 'DDO Kachchh'
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_count INT NOT NULL DEFAULT 0,
    format VARCHAR(10) NOT NULL DEFAULT 'CSV',         -- 'CSV', 'JSON', 'FHIR_NDJSON'
    checksum_sha256 VARCHAR(64) NOT NULL,              -- Cryptographic integrity hash
    is_anonymized BOOLEAN NOT NULL DEFAULT FALSE,       -- Must be TRUE for district-level NPCCHH reports
    file_path VARCHAR(255)
);

-- ============================================================================
-- PRIVACY-PRESERVING AGGREGATE VIEWS (DPDP Act 2023 Compliant)
-- District authorities (DDO, Collectorate, Health Dept) CANNOT view individual
-- worker records without clinical role privileges. They query these views only!
-- ============================================================================

-- 1. Anonymous Taluka Heat & Risk Map View
CREATE VIEW district_taluka_heat_summary AS
SELECT 
    s.taluka,
    s.site_type,
    COUNT(DISTINCT s.site_id) AS total_active_sites,
    COUNT(DISTINCT w.worker_id) AS total_monitored_workers,
    ROUND(AVG(de.avg_wbgt_c), 2) AS mean_wbgt_c,
    ROUND(MAX(de.max_wbgt_c), 2) AS peak_wbgt_c,
    ROUND(SUM(de.hours_above_wbgt_30), 1) AS total_hours_above_30c_wbgt,
    SUM(CASE WHEN de.flag_over_exposure = 1 THEN 1 ELSE 0 END) AS total_overexposed_worker_days,
    SUM(CASE WHEN s.has_potable_water = 0 THEN 1 ELSE 0 END) AS sites_lacking_drinking_water
FROM sites s
LEFT JOIN workers w ON s.site_id = w.current_site_id AND w.consent_given = 1
LEFT JOIN daily_exposure de ON w.worker_id = de.worker_id AND de.shift_date = CURRENT_DATE
GROUP BY s.taluka, s.site_type;

-- 2. Anonymous Health Van Route Prioritization View
CREATE VIEW district_anonymous_risk_summary AS
SELECT 
    s.site_id,
    s.site_name,
    s.taluka,
    s.site_type,
    s.latitude,
    s.longitude,
    COUNT(DISTINCT w.worker_id) AS worker_count,
    COUNT(DISTINCT c.case_id) AS workers_pending_screening,
    ROUND(AVG(de.avg_pm2_5_ug_m3), 1) AS site_avg_pm2_5,
    ROUND(AVG(de.avg_wbgt_c), 1) AS site_avg_wbgt,
    -- Priority Score: weights pending cases, high dust, high heat, and lack of water
    (COUNT(DISTINCT c.case_id) * 3 + 
     CASE WHEN AVG(de.avg_wbgt_c) >= 30.0 THEN 5 ELSE 0 END +
     CASE WHEN s.has_potable_water = 0 THEN 4 ELSE 0 END) AS van_dispatch_priority_rank
FROM sites s
JOIN workers w ON s.site_id = w.current_site_id
LEFT JOIN cases c ON w.worker_id = c.worker_id AND c.status = 'PENDING_SCREENING'
LEFT JOIN daily_exposure de ON w.worker_id = de.worker_id AND de.shift_date = CURRENT_DATE
GROUP BY s.site_id, s.site_name, s.taluka, s.site_type, s.latitude, s.longitude, s.has_potable_water;

-- 3. Worker-Level Van Due List (Restricted to Authorized Mobile Van Medical Teams)
CREATE VIEW workers_due_for_screening_view AS
SELECT 
    w.worker_id,
    w.eshram_uan,
    w.first_name,
    w.last_name,
    w.gender,
    w.age,
    w.job_role,
    s.site_name,
    s.taluka,
    c.case_id,
    c.case_type,
    c.priority_score,
    c.assigned_facility,
    de.cumulative_dust_dose_mg_m3_hr,
    de.hours_above_wbgt_30
FROM workers w
JOIN sites s ON w.current_site_id = s.site_id
JOIN cases c ON w.worker_id = c.worker_id
LEFT JOIN daily_exposure de ON w.worker_id = de.worker_id AND de.shift_date = CURRENT_DATE
WHERE w.consent_given = 1 
  AND c.status IN ('PENDING_SCREENING', 'VAN_SCHEDULED');
