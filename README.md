# PS000109 – Exposure-Triggered Worker Health Screening (Kachchh)

Seva First Innovation Challenge 2026 · Problem statement **PS000109 – Digital Occupational Health Monitoring for Industrial Workers** (District Development Office, Kachchh).

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Standards: ISO 7243](https://img.shields.io/badge/Standard-ISO%207243%20WBGT-orange.svg)](https://www.iso.org/)
[![Compliance: DPDP Act 2023](https://img.shields.io/badge/Privacy-DPDP%20Act%202023-purple.svg)](https://www.meity.gov.in/)
[![Interoperability: ABDM & e-Shram](https://img.shields.io/badge/Interoperability-ABDM%20%7C%20e--Shram-red.svg)](https://abdm.gov.in/)

**Idea in one line:** A cheap site sensor measures heat and dust → when a worker's exposure crosses a safe limit, they get a Gujarati/Hindi SMS and a check-up is booked through existing government schemes (BOCW Dhanvantari Rath, Salt-Worker Medical Van, ESIC) → the result goes into a record the worker owns (linked to e-Shram & ABHA) → the DDO sees an anonymous district dashboard.

Synopsis due **6 Nov 2026**.

---

## 👥 Team Workload & Ownership

| Person | Subsystem | Ownership & Key Deliverables |
|---|---|---|
| **Neel (You / Agent)** | **Database (Data Layer) & Rules Engine** | Complete schema (`database/schema.sql` - 10 tables), 30-day raw vs. permanent rollup retention policy, DPDP Act 2023 privacy views, ISO 7243 WBGT rules engine, PMS5003 humidity correction, 3 query contracts. |
| **Person 2** | **Wokwi Mockup + Price Model + Device Code** | Wokwi ESP32 circuit simulation, 150 mm matte-black globe specs, PMS5003 & BME280 wiring, offline flash ring buffer, unit price model (< ₹40/worker/yr). |
| **Person 3** | **Government Connections + Public API + Alerts** | 12-digit e-Shram UAN QR card flow, ABHA sandbox HIP/HIU integration, BOCW Dhanvantari Rath & Salt Van CSV export contracts, multilingual alerts (Gujarati & Hindi). |
| **Person 4** | **PPT + Everything That Makes the Pitch Convincing** | Official synopsis PPT, legal basis (Factories Act 41C, OSH Code 2020, Gujarat OHS Rules 2025), epidemiological evidence (Tamil Nadu, Qatar, Saudi, Central America), future roadmap (SEWA heat micro-insurance). |

---

## 🗂️ Folder Map

| Folder | What's inside |
|---|---|
| `database/` | Production ANSI SQL schema (10 tables), DB seeder (1,000 workers across 50 sites), query contracts, retention policy. |
| `rules_engine/` | ISO 7243 WBGT calculator (outdoor & indoor formulas), PMS5003 humidity correction, multi-hazard rules evaluator. |
| `data/raw/` | Original empirical datasets (MSHA respirable dust, Construction PM Alphasense vs Sharp, CPCB Gujarat, OSHA health samples, Open-Meteo Mundra). |
| `data/processed/` | Cleaned and summarized datasets (30-day worker exposure summaries, district taluka risk summaries, CPCB station summaries, OSHA silica summaries). |
| `data/synthetic/` | 1,000-worker synthetic Kachchh cohort with e-Shram UANs and ABHA IDs. |
| `docs/` | In-depth engineering blueprints (`DATABASE_ARCHITECTURE.md`, `DATASET_CATALOG.md`, `TEAM_INTEGRATION_SPEC.md`, `HARDWARE_COST_MODEL.md`, `GOVT_SCHEMES_GUIDE.md`). |
| `docs/papers/` | Open-access peer-reviewed studies (He et al. 2022 dust & lung function; NIOSH 2024 low-cost dust monitors). |
| `charts/` | Pre-rendered visualization charts (CPCB Gujarat PM10 days over limit, OSHA silica by industry, WBGT methods). |
| `scripts/` | Data download and WBGT calculation tools (`get_kutch_data.py`, `wbgt_rebuild.py`). |
| `tests/` | Pytest / unittest test suites for WBGT equations, sensor corrections, and rules triggers. |

---

## 📊 Key Numbers & Public Datasets (With Sources)

| Claim | Number | File / Source |
|---|---|---|
| Silica dust: US worker samples over limit (50 µg/m³) | **26%** of 8-hour samples (599) | `data/processed/osha_silica_summary_by_industry.csv` |
| Gujarat industrial estate dust | Vatva over PM10 limit on **83%** of days vs Gandhinagar 31% (2019–20) | `data/processed/cpcb_gujarat_station_summary.csv` |
| Dust harms lungs | Dust above limit → **~2.5×** odds of abnormal lung function (2,045 workers, China) | `docs/papers/He_2022_dust_exposure_lung_function_China.pdf` |
| Cheap sensors work | <$300 sensors vs ~$5,000 mining monitors, PM10 ≈ respirable dust after calibration | `docs/papers/NIOSH_2024_low_cost_dust_monitors_case_study.pdf` |
| Heat: salt-pan workers over heat limit | **87.5%** over threshold; 48% acute dehydration, 2.1x kidney impairment risk | Tamil Nadu cohort (Venugopal / Jakobsson et al., `data/raw/global_heat_stress_benchmarks.csv`) |
| Construction PM: Optical sensor vs Research OPC | PMS5003 tracks Alphasense OPC-N3 with $R^2 > 0.88$ after humidity correction | `data/raw/construction_pm_alphasense_sharp.csv` (Mendeley Construction PM study) |
| MSHA Respirable Mine Dust Replay | Quarry drillers & crusher operators exceed 1.5 mg/m³ quartz PEL in 24% of shifts | `data/raw/msha_personal_dust_samples_sample.csv` (MSHA Open Data) |

> **Honesty rule:** Public datasets prove the problem exists. They are **not** Kachchh worker data. Never present replayed or foreign data as our own measurements.

---

## 🗄️ Database Architecture (The 10 Core Tables)

1. `sites`: Physical worksites (lat/long, taluka, drinking water, toilets, shade flags).
2. `workers`: Worker identity, 12-digit e-Shram UAN, ABHA ID, QR card hash, consent records.
3. `devices`: Hardware inventory (Site Nodes and Personal Dust Badges).
4. `readings`: High-frequency sensor telemetry (Ta, RH, 150mm Tg, Tnw, WBGT, PM2.5, UV, Noise).
5. `daily_exposure`: Permanent longitudinal shift summaries (cumulative dust dose, hours > 30°C WBGT).
6. `rules`: Multi-hazard thresholds and action payloads.
7. `cases`: Clinical screening workflows (spirometry, creatinine, ILO X-ray tracking).
8. `symptoms`: Daily self-reported symptoms (dark urine, dizziness, cough, eye glare).
9. `alerts`: Dispatched multilingual alerts (English, Gujarati, Hindi) and lamp color commands.
10. `exports`: Cryptographically audited government exports (BOCW, Salt Van, ESIC, NPCCHH).

### The Three Query Contracts (`database/queries.py`):
- **`get_workers_due_for_checkup()`**: Generates prioritized mobile van screening rosters based on 30-day cumulative dust dose ($> 2.5\text{ mg/m}^3\cdot\text{hr}$) or severe heat strain ($> 15\text{ hrs} > 30^\circ\text{C}$ with dark urine).
- **`get_site_risk_today()`**: Real-time WBGT, required ISO 7243 work-rest schedule, visual lamp status, and potable water/toilet violations.
- **`get_hotspots_by_job()`**: Cross-job hazard rankings (Crusher operators lead in respiratory symptoms; salt rakers lead in thermal strain and dark urine).

---

## 🌡️ How WBGT & Dust Corrections Are Calculated

### 1. Outdoor WBGT (ISO 7243):
$$WBGT_{\text{outdoor}} = 0.7 \, T_{nw} + 0.2 \, T_g + 0.1 \, T_a$$
*(Calculated using a standard **150 mm matte-black copper globe**; research in Scientific Reports 2022 proved 40mm ping-pong balls underestimate true radiant heat under wind).*

### 2. Coastal Humidity Correction for Optical Dust Sensors:
$$PM_{\text{corrected}} = \frac{PM_{\text{raw}}}{1 + 0.25 \cdot \left(\frac{RH^2}{1 - RH}\right)}$$

### 3. ACGIH Work-Rest Schedules (Heavy Labor):
- **WBGT < 28.0°C**: Continuous work. Lamp = `GREEN`.
- **28.0°C ≤ WBGT < 29.5°C**: 45m work / 15m rest. Lamp = `YELLOW`.
- **29.5°C ≤ WBGT < 31.0°C**: 30m work / 30m rest in shade + ORS. Lamp = `ORANGE`.
- **WBGT ≥ 31.0°C**: 15m work / 45m rest or **STOP HEAVY WORK**. Lamp = `RED`.

---

## 🚀 Quickstart & Verification Commands

```bash
# 1. Initialize and seed the 10-table database (1,000 workers & 50 sites)
python database/init_db.py
python database/seed_data.py

# 2. Test the query contracts (Who's due, Site risk today, Hotspots by job)
python database/test_queries.py

# 3. Run unit tests for WBGT formulas and rules engine
python -m unittest tests/test_rules_engine.py

# 4. Generate or update all CSV datasets
python data/fetch_and_generate_datasets.py
```

---

## 📜 Full Documentation Index

- [`docs/DATABASE_ARCHITECTURE.md`](docs/DATABASE_ARCHITECTURE.md): Database design, ERD, and DPDP Act 2023 compliance.
- [`docs/DATASET_CATALOG.md`](docs/DATASET_CATALOG.md): Source citations, schemas, and replay instructions for all datasets.
- [`docs/TEAM_INTEGRATION_SPEC.md`](docs/TEAM_INTEGRATION_SPEC.md): Specifications for Person 2 (Hardware), Person 3 (API/Govt), and Person 4 (Pitch/Evidence).
- [`docs/HARDWARE_COST_MODEL.md`](docs/HARDWARE_COST_MODEL.md): Bill of materials, ₹2,015 site node, and Kenzen competitor cost comparison.
- [`docs/GOVT_SCHEMES_GUIDE.md`](docs/GOVT_SCHEMES_GUIDE.md): Integration guide for BOCW Dhanvantari Rath, Salt Pan Vans, e-Shram, and ABHA.
