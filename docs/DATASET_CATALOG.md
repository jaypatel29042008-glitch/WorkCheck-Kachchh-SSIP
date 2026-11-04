# 📚 Occupational Hazard Dataset Catalog & Replay Guide
## PS000109: Exposure-Triggered Worker Health Screening (Kachchh District)

This catalog indexes the empirical datasets, real-time sensor time series, and epidemiological cohorts incorporated into this repository.

---

## 1. Directory Structure

```
data/
├── raw/
│   ├── kachchh_weather_heat_2024_2025.csv       # Hourly meteorological & WBGT data (Mundra/Kandla)
│   ├── msha_personal_dust_samples_sample.csv   # MSHA respirable dust & quartz shift samples
│   ├── construction_pm_alphasense_sharp.csv    # 2-sec real-time PM comparison (Alphasense vs Sharp/PMS5003)
│   ├── osha_silica_cement_quarry_limits.csv    # OSHA & Indian Factories Act statutory standards
│   └── global_heat_stress_benchmarks.csv       # Tamil Nadu, Saudi, Qatar, Central America cohorts
├── processed/
│   ├── worker_exposure_daily_summary.csv       # Longitudinal daily exposure rollups (1,000 workers)
│   └── district_anonymized_risk_summary.csv     # Anonymized district taluka heatmap aggregations
└── synthetic/
    └── kachchh_salt_pan_workers_cohort.csv      # 1,000 workers with e-Shram UANs and ABHA IDs
```

---

## 2. Dataset Specifications

### 1. Kachchh Real Meteorological & WBGT Telemetry
- **File**: `data/raw/kachchh_weather_heat_2024_2025.csv`
- **Source**: Open-Meteo Historical Archive API (Coordinates: `22.74°N, 69.70°E` - Mundra Port & Coastal Salt Belt).
- **Parameters**: Dry-bulb ambient temperature (°C), relative humidity (%), solar irradiance (W/m²), wind speed (m/s), estimated natural wet-bulb (°C), 150mm matte-black globe temperature (°C), and calculated outdoor/indoor WBGT (°C).
- **Utility**: Provides the empirical heatwave foundation for calculating shift heat strain and proving the necessity of ISO 7243 work-rest cycles in Kachchh.

### 2. MSHA Respirable Dust & Personal Health Replay Dataset
- **File**: `data/raw/msha_personal_dust_samples_sample.csv`
- **Source**: US Mine Safety and Health Administration (MSHA) Open Data.
- **Fields**: `sample_id`, `occupation_title`, `respirable_dust_concentration_mg_m3`, `quartz_silica_pct`, `shift_duration_minutes`, `mask_worn`, `violation_flag`.
- **Occupations Mapped**:
  - Rock Driller (Stone Quarry)
  - Crusher Operator (Aggregate Plant)
  - Cement Bulk Loader
  - Haulage Truck Driver
  - Salt Pumping & Evaporation Raker
- **Utility**: Used to replay realistic worn-badge continuous dust profiles during shifts without relying on unvalidated synthetic numbers.

### 3. Construction PM Dataset (Optical Sensor Comparison)
- **File**: `data/raw/construction_pm_alphasense_sharp.csv`
- **Source**: Mendeley Construction PM Dataset & AQICN PMS5003 experimental studies.
- **Resolution**: 2-second sampling interval (1,800 time steps / 1 hour continuous work).
- **Key Finding & Correction**: Demonstrates how optical particle sensors (Sharp GP2Y / PMS5003) overestimate particulate concentrations under high coastal humidity (> 60% RH) due to hygroscopic aerosol growth. Validates the `SensorCorrection.correct_pms5003_humidity()` algorithm.

### 4. OSHA Statutory Standards & Indian Factories Act
- **File**: `data/raw/osha_silica_cement_quarry_limits.csv`
- **Source**: OSHA 29 CFR 1910.1053, NIOSH REL, and Gujarat Factories Rules under Factories Act 1948 Section 41C.
- **Benchmarks**:
  - Respirable Crystalline Silica: OSHA PEL = 50 µg/m³, Action Level = 25 µg/m³, Indian Factories Act = 100 µg/m³.
  - Portland Cement Total Dust: OSHA PEL = 15 mg/m³, ACGIH TLV = 1 mg/m³.
- **Statutory Mandate**: Triggers mandatory annual medical surveillance (spirometry and ILO-classified chest radiography).

### 5. Global Occupational Heat Stress & CKDu Benchmarks
- **File**: `data/raw/global_heat_stress_benchmarks.csv`
- **Cohorts Included**:
  1. **Tamil Nadu Salt-Pan Cohort** (*Dr. Vidhya Venugopal, Sri Ramachandra University*): 512 workers, mean WBGT 31.5°C, 48% acute clinical dehydration, 2.1x elevated risk of impaired renal eGFR.
  2. **Saudi Construction Worker Wearables Study** (*arXiv 2023*): 19 workers monitored via Garmin trackers and site microclimate nodes (~95% accuracy in heat strain classification).
  3. **Qatar Supreme Committee Stadium Workers** (*Lucas et al., ILO*): Mandatory work stoppage at WBGT ≥ 32.0°C reduced heat emergency hospitalizations by 72%.
  4. **Central America Sugarcane Cutters (WE-Program)**: Chronic kidney disease of non-traditional origin (CKDu) mitigated by structured water-rest-shade schedules.
  5. **TISS / Heat Watch Gujarat Survey (2026)**: 115 workers surveyed; 87% heat symptoms, 73% lacked clean drinking water on site, 45% had dark urine.

---

## 3. How to Replay Datasets Through the System

You can stream these datasets into the database or test the rules engine using:
```bash
# Replay full dataset generation and database seeding
python data/fetch_and_generate_datasets.py
python database/seed_data.py

# Verify query outputs and clinical check-up due lists
python database/test_queries.py
```
