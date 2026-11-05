# 📱 Master Dashboard Website Architecture & ABHA Publishing Data Plan
## PS000109: Exposure-Triggered Worker Health Screening & Digital ABHA Health Locker

---

## 🎯 1. Executive Vision & Core Objective

The core objective is to build a **production-grade digital occupational health platform** that:
1. **Continuously monitors microclimate & occupational hazards** (outdoor WBGT, respirable silica dust, UV glare) across industrial worksites in Kachchh district.
2. **Captures worker health symptoms and clinical examination outcomes** (spirometry $FEV_1/FVC$, serum creatinine, urine specific gravity, chest X-rays).
3. **Publishes verified clinical screening records directly into the worker's official ABHA ID** (Ayushman Bharat Health Account) under the Ayushman Bharat Digital Mission (ABDM), creating an immutable, portable, worker-owned digital health record linked to their **12-digit e-Shram UAN**.
4. **Delivers an intuitive multi-persona web dashboard** serving:
   - **Informal Laborers** (Multilingual QR Health Pass in Gujarati, Hindi, English)
   - **Worksite Supervisors** (Real-time ISO 7243 work-rest lamp status and hydration reminders)
   - **Mobile Medical Van Doctors** (Clinical diagnostic logging & one-click ABHA publishing)
   - **District Administration (DDO Kachchh)** (Anonymous district heatmaps & mobile van routing)

---

## 🔄 2. End-to-End Data Pipeline Architecture

```mermaid
flowchart TD
    subgraph 1. Exposure & Symptom Ingestion
        SN[ESP32 Site Node<br/>150mm Globe + PMS5003 + UV] -->|MQTT / HTTPS| API[FastAPI Telemetry Ingestion]
        WRK[Worker QR Kiosk / App] -->|Daily Symptom Check-in| API
    end

    subgraph 2. Rules Engine & Risk Trigger
        API --> DB[(Occupational Health DB<br/>PostgreSQL / SQLite)]
        DB --> RE[ISO 7243 Rules Engine]
        RE -->|Cumulative Silica > 2.5 mg/m³·hr<br/>OR WBGT > 30°C + Dark Urine| DUE[Prioritized Health Van Due List]
    end

    subgraph 3. Clinical Screening (Mobile Medical Vans)
        DUE --> VAN[Gujarat BOCW Dhanvantari Rath<br/>Salt-Worker Medical Van]
        VAN -->|Doctor Logs: Spirometry, Creatinine, X-Ray| CLINIC[Screening Station UI]
    end

    subgraph 4. ABDM Milestone 2 (M2) Publishing Engine
        CLINIC --> ABDM[services/abdm_publisher.py]
        ABDM -->|Builds Standard HL7 FHIR R4 Bundle| FHIR[FHIR DiagnosticReport<br/>+ Patient + Observations]
        FHIR -->|SHA-256 Signed & CareContext Linked| GW[ABDM Gateway Sandbox]
    end

    subgraph 5. Worker-Owned Digital Locker
        GW -->|Deposited into Personal Health Record| ABHA[Worker's ABHA PHR Locker<br/>e.g., worker@abdm]
        ABHA -->|Access Anywhere in India via e-Shram UAN| PHR[ABHA Mobile App / SMS Link]
    end
```

---

## 🏛️ 3. ABDM (Ayushman Bharat Digital Mission) FHIR R4 Data Contract

Our system acts as a registered **Health Information Provider (HIP)** under ABDM Milestone 2 (M2). When the mobile van doctor completes an occupational screening, the system bundles and publishes the following structured FHIR R4 resources:

### Standard Resources in the Published Bundle:
1. **`Composition`**: Document header declaring an "Exposure-Triggered Occupational Health Examination".
2. **`Patient`**: Maps the worker's **ABHA ID** (`91-XXXX-XXXX-XXXX`), **ABHA Address** (`name@abdm`), and **12-digit e-Shram UAN** (`1000XXXXXXXX`).
3. **`Practitioner`**: Authenticates the screening medical officer's state medical council registration number (e.g. `GMC-KUTCH-MD-4081`).
4. **`Observation` (Respiratory Spirometry)**:
   - LOINC `19926-5` ($FEV_1/FVC$ ratio). Values $< 0.70$ flag airway obstruction.
   - LOINC `20150-9` ($FEV_1$ liters) and LOINC `19868-9` ($FVC$ liters).
5. **`Observation` (Renal & Dehydration)**:
   - LOINC `2160-0` (Serum Creatinine in $\text{mg/dL}$). Flags potential acute kidney strain if $> 1.3\text{ mg/dL}$.
   - LOINC `5811-5` (Urine Specific Gravity). Flags dehydration if $\ge 1.020$.
6. **`DiagnosticReport`**:
   - Master report status `final`.
   - International Labour Organization (**ILO**) Chest Radiography pneumoconiosis grading (`0/-`, `1/0`, `1/1`, `2/2`, progressive massive fibrosis).
   - SNOMED-CT clinical coding for diagnostic conclusions (e.g., `415560003` for suspected silicosis).
7. **`CareContext` Linking**:
   - Registers a unique context (e.g., `CARE-CTX-20261105-0012`) under the worker's ABHA address, allowing instant retrieval via any ABDM-compliant PHR application (e.g., ABHA App, Aarogya Setu, Paytm Health).

---

## 🖥️ 4. The 4 Core Dashboard Interfaces

### View 1: Worker Health Pass & ABHA Locker Portal (`/worker/[id]`)
- **Primary Audience**: Informal laborers, salt-pan rakers, quarry drillers.
- **Languages**: Gujarati (`gu`), Hindi (`hi`), English (`en`).
- **Core Features**:
  - **Color-Coded Status Card**: Clear visual health indicator (Green = Up to Date; Yellow = Screening Recommended; Red = Urgent Health Van Visit Required).
  - **ABHA Sync Status**: Displays linked ABHA address (`ramesh.ahir@abdm`) and verification badge.
  - **Personal Exposure Thermometer**: Shows recent shifts worked in hazardous conditions and cumulative dust score in simple visual iconography.
  - **One-Touch Symptom Self-Reporting**: Visual buttons for logging dark urine, dizziness, extreme thirst, chronic cough, and salt-glare eye burning.
  - **Direct ABHA Download**: Button to download official verified PDF screening certificate with QR code for employment anywhere in India.

---

### View 2: Worksite Live Watch & ISO 7243 Lamp Supervisor (`/site/[id]`)
- **Primary Audience**: Worksite supervisors, safety officers at salt pans, quarries, cement plants.
- **Core Features**:
  - **Live Environmental Gauges**: Real-time display of Ambient Temp ($T_a$), Relative Humidity ($RH\%$), 150mm Globe Temp ($T_g$), and Calculated Outdoor WBGT.
  - **Visual ISO 7243 Lamp State**: Giant color status badge (`GREEN` / `YELLOW` / `ORANGE` / `RED`) matching the physical on-site Neopixel lamp.
  - **Active Work-Rest Timer**: Countdown clock for mandatory shaded breaks (e.g. *"30 min work completed — 30 min shaded rest mandatory now"*).
  - **Infrastructure Compliance Checklist**: Daily mandatory toggle:
    - [x] Potable drinking water container filled?
    - [x] ORS electrolyte packets distributed?
    - [x] Shaded canopy rest shelter accessible?
    - [x] Sanitation latrines operational?
  - **Worker Attendance & QR Scanner**: Quick camera-based scanning of worker QR badges.

---

### View 3: Mobile Medical Van Screening & ABHA Publishing Station (`/van/screening`)
- **Primary Audience**: Screening doctors and nurses aboard the **Gujarat BOCW Dhanvantari Arogya Rath** and **Salt-Worker Medical Vans**.
- **Core Features**:
  - **Van Route Priority Queue**: Workers queued automatically in order of occupational exposure severity ($5/5$ critical priority first).
  - **Fast Clinical Data Entry**:
    - Spirometry input: $FEV_1$, $FVC$, auto-calculated $FEV_1/FVC$ ratio.
    - Renal biomarkers: Urine Specific Gravity and Serum Creatinine.
    - Chest X-Ray: ILO Category selector (`0/-`, `1/0`, `1/1`, `2/1`, `2/2`, `3/3`, `PMF`).
    - Clinical notes & doctor registration number.
  - **One-Click "Publish to ABHA ID" Button**:
    - Generates HL7 FHIR R4 bundle in background.
    - Calculates SHA-256 cryptographic checksum.
    - Pushes CareContext to ABDM Gateway.
    - Automatically sends SMS notification to worker in Gujarati/Hindi:
      *"તમારો આરોગ્ય તપાસ રિપોર્ટ સફળતાપૂર્વક તમારા આભા (ABHA) એકાઉન્ટમાં જમા થઈ ગયો છે."*

---

### View 4: District Administration (DDO Kachchh) Macro Heatmap (`/district/overview`)
- **Primary Audience**: District Development Officer (DDO Kachchh), Chief District Health Officer (CDHO), Labour Commissioner.
- **Compliance**: **100% DPDP Act 2023 Compliant** (No worker names, no e-Shram UANs, zero individual clinical history displayed).
- **Core Features**:
  - **Interactive District Geographic Map**: Taluka-level polygon visualization of Kachchh (Mundra, Anjar, Bhuj, Gandhidham, Mandvi) showing:
    - High-heat zones (hours exceeding WBGT 30°C).
    - Particulate matter hotspots (quarry clusters exceeding $PM_{10}$ standards).
    - Water and toilet deficit clusters.
  - **Mobile Medical Van Fleet Tracker**: Live tracking of Dhanvantari Arogya Rath vans and Salt-Worker vans with coverage percentages.
  - **Statutory Export Engine**: One-click generation of:
    - Gujarat BOCW Welfare Board Due Lists (`.csv`)
    - Industries Commissionerate Salt Pan Van Priority Rosters (`.csv`)
    - NPCCHH Weekly Heat Illness Surveillance Reports (`.json`)
    - ESIC Referral Batches

---

## 🛠️ 5. Modern Frontend & Backend Tech Stack (5-Tool Vibe Coding)

| Layer | Technology | Key Capabilities & Rationale |
|---|---|---|
| **Frontend Framework** | **Next.js 15+ (App Router) / React 19** | Server components for instantaneous page loads; high-speed mobile responsiveness. |
| **Styling & Design** | **Tailwind CSS + shadcn/ui** | Clean, accessible design system; high-contrast modes for outdoor sunlight visibility. |
| **Typography & Theme** | **Inter / Plus Jakarta Sans + Noto Sans Gujarati** | Anti-AI-slop typography with native Gujarati script rendering. |
| **Visual Indicators** | **Framer Motion + Canvas Shaders** | Dynamic animated WBGT thermal gauges and smooth work-rest countdown progress rings. |
| **Geographic Mapping** | **Leaflet / React-Leaflet** | Lightweight offline-capable vector maps of Kachchh district and worksite coordinates. |
| **Backend & APIs** | **FastAPI (Python 3.11+)** | High-throughput asynchronous endpoints with auto-generated Swagger UI (`/docs`). |
| **Database** | **SQLite (Local Dev) / PostgreSQL (Prod)** | Tiered architecture with 30-day raw partition and permanent daily rollups. |
| **ABDM Standards** | **HL7 FHIR Release 4 (R4)** | Strict compliance with National Health Authority (NHA) DiagnosticReport schema. |

---

## 📅 6. Serialized Execution Roadmap (`TASKS.md`)

- [x] **Milestone 1**: Compile and verify all 35 real datasets (MSHA, Open-Meteo, PMC10334398 Salt Pan Cohort, SilicoData).
- [x] **Milestone 2**: Build the 10-table database schema, seeder (1,000 workers across 50 sites), and 3 query contracts.
- [x] **Milestone 3**: Implement ISO 7243 WBGT calculator, 150mm globe equations, and PMS5003 humidity correction.
- [x] **Milestone 4**: Architect the ABDM / ABHA FHIR R4 Publishing Engine (`services/abdm_publisher.py`).
- [ ] **Milestone 5**: Implement the FastAPI backend server (`app/main.py`) exposing the 4 role-based API endpoints.
- [ ] **Milestone 6**: Build the high-fidelity responsive Dashboard Website with the 4 distinct user interfaces.
- [ ] **Milestone 7**: Integrate Wokwi ESP32 hardware telemetry stream and test end-to-end publishing into ABHA Sandbox.
