# PS000109 – Exposure-Triggered Worker Health Screening (Kachchh)

Seva First Innovation Challenge 2026 · Problem statement **PS000109 – Digital Occupational Health Monitoring for Industrial Workers** (District Development Office, Kachchh).

**Idea in one line:** a cheap site sensor measures heat and dust → when a worker's exposure crosses a safe limit, they get a Gujarati/Hindi SMS and a check-up is booked through existing government schemes → the result goes into a record the worker owns (linked to e-Shram) → the DDO sees an anonymous district dashboard.

Synopsis due **6 Nov 2026**.

---

## Folder map

| Folder | What's inside |
|---|---|
| `data/raw/` | Original files, unchanged (small ones only). See `data/SOURCES.md`. |
| `data/processed/` | Cleaned files we made from the raw data. Use these. |
| `charts/` | Ready-made charts for the synopsis / PPT. |
| `scripts/` | Python scripts to download and calculate data. |
| `db/` | Database schema and rules (owner: Neel). |
| `docs/papers/` | Open-access papers we rely on. |

Big files (the 2.5 GB OSHA download etc.) are **not** in git. `data/SOURCES.md` says where to get them.

---

## Key numbers (with sources)

| Claim | Number | File / source |
|---|---|---|
| Silica dust: US worker samples over limit (50 µg/m³) | **26%** of 8-hour samples (599) | `data/processed/osha_silica_summary_by_industry.csv` |
| Gujarat industrial estate dust | Vatva over PM10 limit on **83%** of days vs Gandhinagar 31% (2019–20) | `data/processed/cpcb_gujarat_station_summary.csv` |
| Dust harms lungs | Dust above limit → **~2.5×** odds of abnormal lung function (2,045 workers, China) | `docs/papers/He_2022_...pdf` |
| Cheap sensors work | <$300 sensors vs ~$5,000 mining monitors, PM10 ≈ respirable dust after a lab check | `docs/papers/NIOSH_2024_...pdf` |
| Heat: salt-pan workers over heat limit | **87.5%** (Tamil Nadu, Jakobsson et al. 2023) | paper, see SOURCES |
| Heat: Kachchh working hours over limit | *run `scripts/` – pending* | `data/hourly_*_wbgt_methods.csv` |

**Honesty rule:** public datasets prove the problem exists. They are **not** Kachchh worker data. Never present replayed or foreign data as our own measurements.

---

## How to run

```bash
pip install numpy pandas matplotlib requests thermofeel pythermalcomfort

# 1. Download Kachchh heat + dust (Open-Meteo, free, no key) -> data/
cd scripts
python get_kutch_data.py

# 2. WBGT checks, worked example, method chart
python wbgt_rebuild.py

# 3. WBGT for every hour at a site (sun / shade / simple)
python wbgt_rebuild.py data/hourly_mundra_port.csv
```

## How WBGT is calculated (summary)

WBGT = heat-stress score from 3 thermometers: wet wick (`Tnwb`), black globe (`Tg`), air (`Ta`).

- **ISO 7243 (meter):** outdoor `0.7·Tnwb + 0.2·Tg + 0.1·Ta`, shade `0.7·Tnwb + 0.3·Tg`
- **Bernard (our site node):** estimate `Tnwb` from air temp, humidity, wind and globe, then the ISO formula
- **Liljegren (weather data, in sun):** full physics model (via `thermofeel`)
- **ABOM (screening only):** temperature + humidity

Safe limits (ACGIH): **27.5 °C** heavy work, **28 °C** moderate work. Details and checks are in `scripts/wbgt_rebuild.py`.

---

## Team

| Person | Owns |
|---|---|
| Neel | Database, data pipeline, rules |
| Person 2 | Wokwi device mock-up, cost model, device code |
| Person 3 | Government system connections (e-Shram, ABHA, schemes), public API |
| Person 4 | PPT / synopsis, future scope |
