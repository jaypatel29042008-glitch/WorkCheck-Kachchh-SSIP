# Data sources and licences

Every file in `data/` and `docs/` is listed here. Credit the source whenever a number is used.

## In this repo

| File(s) | What it is | Source | Licence |
|---|---|---|---|
| `raw/indian_salt_pan_workers_clinical_cohort_real.csv` | Real clinical cohort of 352 Indian salt-pan workers: WBGT, cross-shift body temp, water intake (median 1.0L), USG dehydration (28%), eGFR and CKD staging (7% < 60 ml/min) | Venugopal, Lennqvist, Jakobsson et al. 2023, *Kidney International Reports*, PMC10334398 | CC BY-NC-ND |
| `raw/silicodata_indian_quarry_workers_clinical_real.csv` | Real clinical cohort of 445 Indian stone quarry & crusher workers: years in quarrying, ILO pneumoconiosis classification, FEV1, FVC, FEV1/FVC ratios | Akhter, Ranjan et al. 2025 (IIT Jodhpur / Nature *Scientific Data* 12:5595) | CC BY 4.0 |
| `raw/msha_personal_health_samples_real.csv` | 600 real respirable dust & crystalline silica samples across quarry drillers, crusher operators, and cement loaders | US Department of Labor, Mine Safety and Health Administration (MSHA) Open Government Data | Public Domain |
| `hourly_*.csv` (`bhuj`, `kandla_port`, `mundra_port`, `little_rann_kutch`, `abdasa_cement`) | Real multi-parameter hourly weather (ERA5) and air quality (CAMS model: PM10, PM2.5, dust) for 5 Kachchh industrial clusters | Open-Meteo European Weather Archive & Copernicus CAMS Model | CC BY 4.0 / Open Access |
| `monthly_summary.csv` | Monthly aggregations of heatwave work-hours (WBGT >= 28C, 30C, 32C) and high-dust days for Kachchh | Computed by `scripts/download_all_datasets.py` from Open-Meteo | CC BY 4.0 |
| `processed/mendeley_construction_pm_*.csv` | Real 10-minute moving averages of Alphasense OPC-N2 vs Sharp optical PM sensor during active mortar mixing and concrete cutting | Mendeley Data `wy6shdctsr` – https://data.mendeley.com/datasets/wy6shdctsr | CC BY 4.0 |
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
| MSHA Coal Dust Samples / Personal Health Samples bulk dumps | varies | https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp |
| Firefighter heat-strain data (core temp, heart rate) | small | https://data.mendeley.com/datasets/7ghxcsd9sz (CC BY 4.0) |

## Key papers (not stored, cite by link)

- Jakobsson et al. 2023, *Occupational Heat Stress and Kidney Health in Salt Pan Workers*, Kidney Int Rep – Tamil Nadu WBGT and kidney data. https://pmc.ncbi.nlm.nih.gov/articles/PMC10334398
- Akhter, Ranjan et al. 2025, *Silicodata: An Annotated Benchmark CXR Dataset for Silicosis Detection*, Nature Scientific Data 12:5595. https://doi.org/10.1038/s41597-024-04186-0
- Lemke & Kjellstrom 2012, *Calculating Workplace WBGT from Meteorological Data*, Industrial Health 50:267 – the WBGT methods we rebuilt. https://www.jniosh.johas.go.jp/en/indu_hel/doc/IH_50_4_267.pdf
- Sousan, Mizelle et al. 2026, wearables for heat risk in agricultural workers, Am J Ind Med (NIOSH). https://stacks.cdc.gov/view/cdc/259990
