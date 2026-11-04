# 🤝 Team Integration & Subsystem Handover Specification
## PS000109: Exposure-Triggered Worker Health Screening (Kachchh District)

This document defines the clear technical interfaces, schemas, and deliverables for each team member to ensure seamless integration.

---

## 1. Person 2: Wokwi Hardware Simulation & Unit Price Model

### Responsibilities:
1. **Wokwi ESP32 Circuit Simulation**:
   - Build and test an online Wokwi ESP32 circuit simulation representing:
     - **Ambient Site Node**: ESP32, BME280 (I2C: 0x76), PMS5003 stand-in (UART RX/TX or Potentiometer ADC stand-in), Neopixel RGB LED lamp (GPIO 18), and 150mm Black Globe Thermistor (NTC ADC pin).
     - **Personal Dust Badge**: ESP32-C3 / Xiao ESP32, dust sensor input, INMP441 microphone stand-in, vibration sensor, and offline flash ring buffer.
2. **Device Firmware (ESP32 C++ / Arduino / MicroPython)**:
   - **Sampling Loop**: Read sensors every 10 seconds; compute average over 1 minute.
   - **Offline Buffering**: When WiFi/GSM connectivity drops, store readings into SPIFFS/LittleFS ring buffer. When network restores, upload with `is_offline_buffered = TRUE`.
   - **Colored Lamp Control**:
     - `GREEN`: Continuous work (WBGT < 28°C)
     - `YELLOW`: 45m work / 15m rest (28°C ≤ WBGT < 29.5°C)
     - `ORANGE`: 30m work / 30m rest (29.5°C ≤ WBGT < 31.0°C)
     - `RED`: 15m work / 45m rest or STOP WORK (WBGT ≥ 31.0°C)
3. **150 mm Globe Finding (Scientific Reports 2022)**:
   - *Do not use a 40mm ping-pong ball*. Scientific Reports (2022) proved 40mm balls have an R² of only 0.65 vs 0.92 for a 150mm standard globe, and in wind they read almost identically to air temperature.
   - *BOM Choice*: Use a 150 mm hollow copper or aluminum float ball painted matte black (~₹450).
4. **Unit Price Model**:
   - **Site Node Unit Cost**: ~₹2,050 (ESP32 ₹350 + BME280 ₹250 + PMS5003 ₹800 + 150mm Globe ₹450 + Housing/Solar ₹200).
   - **Personal Dust Badge Unit Cost**: ~₹1,450.
   - **Annual Cost Per Worker**: **< ₹40/worker/year** (amortized over 50 sites and 1,000 workers).
   - **Competitor Comparison**: Kenzen charges $50/worker/month (~₹4,100/mo); industrial dust monitors cost ₹5,00,000+.

---

## 2. Person 3: Government Systems Integration, Public API & Multilingual Alerts

### Responsibilities:
1. **Government Schemes Integration**:
   - **e-Shram UAN Integration**: Store 12-digit UAN as worker ID on QR card. Records follow the worker anywhere in India.
   - **ABDM / ABHA Sandbox Flow**: Register platform as a Health Information Provider (HIP) and Health Information User (HIU). Screening results upload directly into the worker's ABHA health locker.
   - **Gujarat BOCW Welfare Board**:
     - Total Health Check-up Scheme & Dhanvantari Arogya Rath (mobile van).
     - Automated CSV export: `exports/bocw_van_due_list.csv` feeding the van route schedule.
     - Assistance for Occupational Diseases flagging (Silicosis assistance).
   - **Salt-Worker Welfare Medical Van**: Industries Commissionerate priority routing.
   - **ESIC Routing**: Link insured port and factory workers to ESIC dispensaries (following Gujarat High Court Oct 2026 ruling).
   - **NPCCHH Heat-Illness Surveillance**: Anonymous weekly totals feeding the district report.
2. **Public API (FastAPI Backend)**:
   - Provide FastAPI backend with auto-generated Swagger UI (`/docs`).
   - Core Endpoints:
     - `POST /api/v1/telemetry/readings`: Ingest high-frequency readings from ESP32 nodes.
     - `GET /api/v1/workers/due-for-checkup`: Return prioritized due list for mobile vans.
     - `GET /api/v1/sites/{site_id}/risk-today`: Real-time WBGT, lamp color, and water compliance.
     - `GET /api/v1/district/heat-report`: Anonymized taluka heat rollup for DDO Kachchh.
   - Security: API Keys for site nodes; JWT for supervisors and medical van staff.
3. **Multilingual Alert Dispatch**:
   - Automated SMS and IVR alerts in **Gujarati** (`gu`) and **Hindi** (`hi`).

---

## 3. Person 4: Pitch Deck, Synopsis PPT & Legal Evidence

### Responsibilities:
1. **Synopsis PPT (Official Format)**:
   - Slide 1: Problem Statement (Kachchh climate extremes, 50°C summer heat, coastal humidity, respirable silica in stone crushers, salt glare).
   - Slide 2: Proposed Solution (Exposure-triggered screening, not expensive full-time wearables).
   - Slide 3: Hardware Architecture (ESP32 site nodes, 150mm black globe, optical PMS5003 with humidity correction).
   - Slide 4: Data Layer & Rules Engine (ISO 7243 WBGT, cumulative dust dose, tiered 30-day storage).
   - Slide 5: Government Linkages (e-Shram, ABHA, BOCW Dhanvantari Rath, Salt-Worker Medical Van, ESIC).
   - Slide 6: Unit Economics & Price Model (₹2,000 site node vs $50/mo Kenzen).
   - Slide 7: Evidence & Validation (Kachchh weather script, Tamil Nadu 48% dehydration study, Saudi construction study).
   - Slide 8: Future Roadmap & Scope (SEWA heat micro-insurance, noise, UV, vibration, Morbi ceramics & Surat textiles expansion).
2. **Statutory Legal Backing**:
   - **Factories Act 1948 Section 41C**: Mandatory annual medical examination of workers exposed to toxic/hazardous dust.
   - **Occupational Safety, Health and Working Conditions (OSH) Code 2020**: Mandates clean drinking water, adequate latrines, and free annual medical checkups.
   - **Gujarat Factory Rules & OHS Audit Rules 2025**: Compulsory employer health registers and occupational hygiene audits.
   - **ESI Act Gap**: Highlight that heat stroke is currently *not* recognized as a compensable occupational disease in India; our platform provides the evidence base to change policy.
3. **Key Pitch Hook**:
   > *"Kenzen charges per worker per month for an expensive US arm patch. We give a Kachchh salt pan a ₹2,000 site node, plug into the mobile medical vans Gujarat already operates, and ensure the most vulnerable workers reach them first."*
