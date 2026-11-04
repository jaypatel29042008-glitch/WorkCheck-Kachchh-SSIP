# 🏛️ Government Schemes & Statutory Linkage Guide
## PS000109: Exposure-Triggered Worker Health Screening (Kachchh District)

This guide documents the five government delivery systems, legal codes, and welfare funds our platform connects with.

---

## 1. The Core Operational Strategy

> **"We do not build a redundant worker registry or a parallel healthcare infrastructure. Gujarat already funds mobile health vans and statutory check-ups; our system decides who should use them first based on objective exposure and tracks that they did."**

---

## 2. Government Systems Mapping

### 1. e-Shram National Register of Unorganised Workers
- **Administering Body**: Ministry of Labour & Employment, Govt. of India.
- **Coverage**: Over 31.89 crore informal workers registered nationwide.
- **Integration**:
  - The worker's **12-digit e-Shram Universal Account Number (UAN)** is encoded on the physical QR badge.
  - By using e-Shram UAN as the primary foreign key, the worker's exposure history and health screenings follow them when they migrate between salt pans, quarries, and construction sites anywhere in India.

### 2. ABDM & Ayushman Bharat Health Account (ABHA)
- **Administering Body**: National Health Authority (NHA).
- **Architecture**:
  - Registered as a Health Information Provider (HIP) and Health Information User (HIU) within the ABDM sandbox.
  - Health check-up outcomes (spirometry FEV1/FVC ratios, serum creatinine, ILO chest X-rays) are formatted as FHIR DiagnosticReport resources and deposited directly into the worker's personal ABHA locker.
  - **Worker-Owned Record**: Employers and district officials cannot view clinical details without explicit OTP-based consent.

### 3. Gujarat BOCW Welfare Board (Construction & Quarry Workers)
- **Funding Source**: 1% Construction Cess levied on all building and infrastructure projects in Gujarat.
- **Active Programs Linked**:
  - **Dhanvantari Arogya Rath**: Dedicated mobile medical vans operating across industrial clusters in Gujarat. Our `workers_due_for_screening_view` feeds the van's daily route schedule.
  - **Total Health Check-up Scheme**: Funds comprehensive clinical tests for registered BOCW workers.
  - **Assistance for Occupational Diseases**: Up to ₹3,00,000 compensation for workers diagnosed with silicosis or occupational respiratory diseases.

### 4. Salt-Worker Welfare Scheme (Agarias)
- **Administering Body**: Industries Commissionerate, Govt. of Gujarat.
- **Key Program**: Mobile Medical Vans deployed exclusively for salt-pan workers in the Little Rann of Kutch and coastal Mundra/Gandhidham.
- **Integration**: Our platform identifies salt pans with the highest cumulative WBGT heat hours and darkest urine reports, routing the van to the highest-risk evaporation pans first.

### 5. Employees' State Insurance Corporation (ESIC)
- **Recent Legal Milestone**: Gujarat High Court (October 2026) directed the extension of full ESI coverage across Kutch district (*The Wire*).
- **Integration**: Insured workers at Kandla Port, Mundra SEZ, and cement manufacturing plants who cross hazard thresholds are automatically generated as referral batches for ESIC Dispensaries in Gandhidham and Bhuj.

---

## 3. Statutory & Legal Foundation

| Statute / Regulation | Section / Clause | Mandate | How Our Platform Enforces It |
|---|---|---|---|
| **Factories Act, 1948** | Section 41C | Compulsory pre-employment and annual medical exams for workers in hazardous operations | Flags workers approaching 365 days since last check-up; schedules exam |
| **Occupational Safety, Health and Working Conditions (OSH) Code, 2020** | Section 23 & 24 | Free annual medical check-up; mandatory provision of wholesome drinking water and latrines | Logs water/toilet presence per site; triggers alerts if water is missing during heatwaves |
| **Gujarat Factory Rules** | Schedule XXII | Medical monitoring of workers exposed to free silica and mineral dust | Tracks 30-day cumulative respirable silica dose; triggers chest X-ray and spirometry |
| **Digital Personal Data Protection (DPDP) Act, 2023** | Section 4 & 6 | Notice and consent for processing personal health data | Explicit consent audit logging; district views restricted strictly to anonymous statistical aggregations |
| **NPCCHH Action Plan** | Chapter 4 | National Programme on Climate Change & Human Health: Heat illness surveillance (March–July) | Weekly automated aggregate reporting of heat strain cases to District Surveillance Officer |
