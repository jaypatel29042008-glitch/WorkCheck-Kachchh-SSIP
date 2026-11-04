# 💰 Hardware Cost Model & Bill of Materials (BOM)
## PS000109: Exposure-Triggered Worker Health Screening (Kachchh District)

---

## 1. Unit Bill of Materials (BOM)

### A. Ambient Site Node (Measures WBGT, Dust & UV)
*Installed once per worksite (salt pan cluster, crusher quarry, cement loading zone).*

| Component | Part / Specification | Supplier / Source | Unit Cost (₹) | Bulk Cost (50+ units) |
|---|---|---|---|---|
| Microcontroller | ESP32-WROOM-32 (WiFi + BLE, 30-pin) | Espressif / Robu.in | ₹320 | ₹275 |
| Temperature & Humidity | BME280 Digital Sensor (I2C, ±0.5°C, ±3% RH) | Bosch / Robu.in | ₹260 | ₹220 |
| Black Globe Sensor | 150 mm Hollow Copper Float Ball + 10k NTC Thermistor (Matte Black) | Local Plumbing / Industrial | ₹450 | ₹380 |
| Laser Dust Sensor | PMS5003 Laser Particle Counter (PM1.0, PM2.5, PM10) | Plantower / Robu.in | ₹780 | ₹690 |
| UV Glare Sensor | GUVA-S12SD UV Sensor (Analog 240–370nm) | Roome / ElectronicsComp | ₹140 | ₹110 |
| Visual Indicator | Neopixel WS2812B RGB High-Lumen Lamp Module | Local / Robu.in | ₹80 | ₹60 |
| Power & Enclosure | 5V 2A Solar Panel + 18650 Li-ion + IP65 Weatherproof Box | Generic Industrial | ₹350 | ₹280 |
| **TOTAL SITE NODE COST** | | | **₹2,380** | **₹2,015** |

---

### B. Personal Replay Dust Badge (Worn on Collar/Chest)
*Rotated among representative workers or replayed through synthetic/MSHA feeds.*

| Component | Part / Specification | Supplier / Source | Unit Cost (₹) | Bulk Cost (100+ units) |
|---|---|---|---|---|
| Microcontroller | ESP32-C3 SuperMini (Ultra-compact, BLE 5.0) | Espressif / Robu.in | ₹240 | ₹200 |
| Optical Dust Sensor | PMS5003 or GP2Y1010 Compact Optical Unit | Plantower / Sharp | ₹750 | ₹650 |
| Acoustic Noise Sensor | INMP441 I2S Omnidirectional Digital Microphone | TDK / Robu.in | ₹130 | ₹95 |
| Accelerometer (Vibration) | MPU6050 6-Axis Motion Sensor (for drivers) | InvenSense | ₹110 | ₹85 |
| Battery & Lanyard Clip | 800 mAh LiPo Rechargeable + 3D Printed Case | Local Fabricator | ₹250 | ₹190 |
| **TOTAL DUST BADGE COST** | | | **₹1,480** | **₹1,220** |

---

## 2. District-Wide Deployment Cost Model (Kachchh Pilot)

### Deployment Scope:
- **50 Industrial Worksites** (30 Salt Pans, 10 Stone Crushers, 5 Cement Plants, 5 Port Berths).
- **1,000 Monitored Informal & Contract Workers**.

| Expense Item | Calculation | Year 1 Cost (₹) | Ongoing Annual Cost (₹) |
|---|---|---|---|
| Site Nodes Hardware (50 units) | 50 × ₹2,015 | ₹1,00,750 | ₹10,000 (10% spares) |
| Personal Dust Badges (100 rotating units) | 100 × ₹1,220 | ₹1,22,000 | ₹15,000 (spares) |
| 4G IoT SIM Connectivity | 50 sites × ₹80/month × 12 months | ₹48,000 | ₹48,000 |
| Cloud Database & Server (Lightsail / Free Tier) | SQLite / AWS Lightsail 2GB RAM | ₹12,000 | ₹12,000 |
| QR Code Identification Cards | 1,000 workers × ₹15/card (PVC QR) | ₹15,000 | ₹3,000 (replacements) |
| **TOTAL DISTRICT PILOT COST** | | **₹2,97,750** | **₹88,000** |

### Per-Worker Annual Cost:
$$\text{Year 1 Cost per Worker} = \frac{₹2,97,750}{1,000 \text{ workers}} = \mathbf{₹297.75 \text{ / worker / year}}$$
$$\text{Ongoing Annual Cost per Worker} = \frac{₹88,000}{1,000 \text{ workers}} = \mathbf{₹88.00 \text{ / worker / year (approx ₹7.30 / month)}}$$

---

## 3. Cost Comparison Against Market Alternatives

| Metric | Kenzen Arm Patch (US) | SlateSafety BAND V2 | Industrial Dust Monitor (TSI DustTrak) | **Our Kachchh System (PS000109)** |
|---|---|---|---|---|
| **Hardware Purchase Cost** | Subscription only | ~$800 (~₹66,000) | ₹5,50,000+ | **₹2,015 per site node** |
| **Recurring Cost** | ~$50 / worker / month (~₹4,100) | ~$25 / worker / month | Annual lab calibration (₹50,000) | **₹7.30 / worker / month** |
| **Dust Monitoring** | ❌ Heat only | ❌ Heat only | Dust only (No heat, no WBGT) | ✅ **Combined Dust + WBGT + UV** |
| **Clinical Referral Link**| ❌ Isolated dashboard | ❌ Isolated dashboard | ❌ Raw CSV export only | ✅ **Direct BOCW & Salt Van integration** |
| **Language Support** | English / Spanish | English | English software | ✅ **Gujarati, Hindi, English** |
| **Affordability for Informal Sector**| 0% (Prohibitive) | 0% (Prohibitive) | Only large mining corporations | **100% (Fundable via BOCW Cess)** |
