# Data sources and licences

Every file in `data/` and `docs/` is listed here. Credit the source whenever a number is used.

## In this repo

| File(s) | What it is | Source | Licence |
|---|---|---|---|
| `raw/cpcb_gujarat/Gujarat_*.csv` | Hourly PM2.5, PM10, NO2, O3, SO2 for 5 Gujarat stations (2015–2020; PM10 mostly 2019–20) | CPCB data compiled by Sharma et al., Princeton, "Air Quality in India: Analysis of Surface Air Pollutant Measurements 2015–2019" | CC BY 4.0 |
| `raw/mendeley_construction_pm/DIB_data_Construction_PM.xlsx` | 40 min of 2-second PM readings during concrete mixing and block laying (Alphasense OPC-N2 + Sharp sensors). Check the description tab for units. | Mendeley Data `wy6shdctsr` – https://data.mendeley.com/datasets/wy6shdctsr | CC BY 4.0 |
| `raw/osha_web_queries/sample_data*.txt` | OSHA website query exports (cement, clay, ready-mix, silica) | https://www.osha.gov/opengov/healthsamples | US government, public domain |
| `raw/osha_web_queries/osha_health_samples_dataset_field_definitions.txt` | Column meanings for OSHA data | same | public domain |
| `raw/accidents_ihm_stefanini/*` | 425 industrial accidents, mining/metals, Brazil 2016–17 (injuries, not heat/dust). Used for one point: 58% of injured were contractors. | IHM Stefanini dataset, Kaggle | check Kaggle page before public release |
| `processed/osha_silica_personal_samples_2014_2023.csv` | OSHA personal crystalline-silica samples in µg/m³ (non-blank), with industry group and over-limit flags | made by us from the OSHA bulk download below | public domain |
| `processed/osha_silica_summary_by_industry.csv` | % over action level (25) and limit (50) by industry | made by us | – |
| `processed/cpcb_gujarat_daily_pm.csv`, `cpcb_gujarat_station_summary.csv` | Daily averages and % of days over India's limits (PM10 100, PM2.5 60 µg/m³) | made by us from CPCB files | CC BY 4.0 |
| `docs/papers/NIOSH_2024_low_cost_dust_monitors_case_study.pdf` | Wolfe, Cauda, Yekich, Patts – Real-Time Dust Monitoring with Low-Cost Dust Monitors (NIOSH, 24-079) | CDC Stacks cdc_156297 | US government, public domain |
| `docs/papers/He_2022_dust_exposure_lung_function_China.pdf` | He et al. 2022, Workers' Occupational Dust Exposure and Pulmonary Function, IJERPH 19:11065 | https://doi.org/10.3390/ijerph191711065 | CC BY 4.0 |

## Not in the repo (too big) – download if needed

| Data | Size | Where |
|---|---|---|
| OSHA Chemical Exposure Health Data, full bulk download (1984–2023 XML/CSV + Access DB) | ~2.5 GB | https://www.osha.gov/opengov/healthsamples |
| MSHA Coal Dust Samples / Personal Health Samples (we only have the column definitions) | varies | https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp |
| Open-Meteo hourly Kachchh weather + air quality (made by `scripts/get_kutch_data.py`) | ~30 MB | generated locally |
| Firefighter heat-strain data (core temp, heart rate) – for heat demo | small | https://data.mendeley.com/datasets/7ghxcsd9sz (CC BY 4.0) |

## Key papers (not stored, cite by link)

- Jakobsson et al. 2023, *Occupational Heat Stress and Kidney Health in Salt Pan Workers*, Kidney Int Rep – Tamil Nadu WBGT and kidney data. https://pmc.ncbi.nlm.nih.gov/articles/PMC10334398
- Lemke & Kjellstrom 2012, *Calculating Workplace WBGT from Meteorological Data*, Industrial Health 50:267 – the WBGT methods we rebuilt. https://www.jniosh.johas.go.jp/en/indu_hel/doc/IH_50_4_267.pdf
- Sousan, Mizelle et al. 2026, wearables for heat risk in agricultural workers, Am J Ind Med (NIOSH). https://stacks.cdc.gov/view/cdc/259990
