"""
Download real heat + dust data for Kachchh worksites and summarise it.

Source: Open-Meteo (free, no API key)
  - Weather archive (ERA5 reanalysis): temperature, humidity, sunlight, wind
  - Air quality (CAMS model): PM10, PM2.5, dust

Run:
    pip install requests pandas
    python get_kutch_data.py

Output (in ./data):
    hourly_<place>.csv      every hour, every variable, + estimated WBGT
    monthly_summary.csv     heat-stress hours and high-dust days per month
"""

import math
import time
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# 1. Settings you can change
# ---------------------------------------------------------------------------
START = "2023-01-01"
END = "2026-10-25"          # archive lags real time by a few days

# Approximate coordinates (check on a map and adjust)
PLACES = {
    "bhuj":            (23.25, 69.67),
    "kandla_port":     (23.03, 70.22),
    "mundra_port":     (22.74, 69.70),
    "little_rann_kutch": (23.35, 70.70),   # salt pans, approx.
    "abdasa_cement":   (23.43, 68.85),      # cement belt, approx.
}

# WBGT bands (deg C). APPROXIMATE - replace with ISO 7243 / ACGIH values
# for the workload you care about (heavy work has lower safe limits).
WBGT_BANDS = [28, 30, 32]

# India's 24-hour ambient air standard (NAAQS) - used as a simple "dusty day" flag
PM10_DAY_LIMIT = 100   # micrograms per cubic metre
PM25_DAY_LIMIT = 60

OUT = Path("data")
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 2. Download helpers
# ---------------------------------------------------------------------------
def get_json(url, params, tries=3):
    """GET with a few retries (the free API sometimes rate-limits)."""
    for attempt in range(tries):
        r = requests.get(url, params=params, timeout=60)
        if r.status_code == 200:
            return r.json()
        print(f"  status {r.status_code}, retrying...")
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()


def get_weather(lat, lon):
    data = get_json(
        "https://archive-api.open-meteo.com/v1/archive",
        {
            "latitude": lat, "longitude": lon,
            "start_date": START, "end_date": END,
            "hourly": ("temperature_2m,relative_humidity_2m,shortwave_radiation,"
                       "direct_radiation,wind_speed_10m,surface_pressure"),
            "timezone": "Asia/Kolkata",
        },
    )
    return pd.DataFrame(data["hourly"])


def get_air(lat, lon):
    data = get_json(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        {
            "latitude": lat, "longitude": lon,
            "start_date": START, "end_date": END,
            "hourly": "pm10,pm2_5,dust",
            "timezone": "Asia/Kolkata",
        },
    )
    return pd.DataFrame(data["hourly"])


# ---------------------------------------------------------------------------
# 3. Heat-stress maths
# ---------------------------------------------------------------------------
def vapour_pressure_hpa(temp_c, rh):
    """Actual vapour pressure from temperature and relative humidity."""
    return rh / 100 * 6.105 * math.exp(17.27 * temp_c / (237.7 + temp_c))


def wbgt_abom(temp_c, rh):
    """
    Simple WBGT estimate (Australian Bureau of Meteorology formula).
    Uses only temperature + humidity, assumes moderate sun and light wind.
    It is an APPROXIMATION: real WBGT needs a black-globe reading,
    which our site node will measure.
    """
    return 0.567 * temp_c + 0.393 * vapour_pressure_hpa(temp_c, rh) + 3.94


def wet_bulb_stull(temp_c, rh):
    """Wet-bulb temperature (Stull 2011), for reference."""
    return (temp_c * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(temp_c + rh) - math.atan(rh - 1.676331)
            + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
            - 4.686035)


# ---------------------------------------------------------------------------
# 4. Main loop
# ---------------------------------------------------------------------------
monthly_rows = []

for place, (lat, lon) in PLACES.items():
    print(f"Downloading {place} ...")
    w = get_weather(lat, lon)
    a = get_air(lat, lon)
    df = w.merge(a, on="time", how="left")
    df["time"] = pd.to_datetime(df["time"])

    ok = df["temperature_2m"].notna() & df["relative_humidity_2m"].notna()
    df.loc[ok, "wbgt_est"] = [
        wbgt_abom(t, h) for t, h in zip(df.loc[ok, "temperature_2m"], df.loc[ok, "relative_humidity_2m"])
    ]
    df.loc[ok, "wet_bulb"] = [
        wet_bulb_stull(t, h) for t, h in zip(df.loc[ok, "temperature_2m"], df.loc[ok, "relative_humidity_2m"])
    ]
    df["latitude"], df["longitude"] = lat, lon      # needed by wbgt_rebuild.py
    df.to_csv(OUT / f"hourly_{place}.csv", index=False)

    # daily dust averages -> "dusty day" flags
    daily = df.set_index("time").resample("D").agg({"pm10": "mean", "pm2_5": "mean"})
    daily["pm10_over"] = daily["pm10"] > PM10_DAY_LIMIT
    daily["pm25_over"] = daily["pm2_5"] > PM25_DAY_LIMIT

    # monthly summary
    df["month"] = df["time"].dt.to_period("M")
    daily["month"] = daily.index.to_period("M")
    for month, g in df.groupby("month"):
        d = daily[daily["month"] == month]
        # daytime working hours only (8 am - 6 pm)
        work = g[g["time"].dt.hour.between(8, 17)]
        row = {
            "place": place,
            "month": str(month),
            "max_temp_c": round(g["temperature_2m"].max(), 1),
            "max_wbgt_est_c": round(g["wbgt_est"].max(), 1),
        }
        for b in WBGT_BANDS:
            row[f"work_hours_wbgt_ge_{b}"] = int((work["wbgt_est"] >= b).sum())
        row["days_pm10_over_limit"] = int(d["pm10_over"].sum())
        row["days_pm25_over_limit"] = int(d["pm25_over"].sum())
        row["days_with_dust_data"] = int(d["pm10"].notna().sum())
        monthly_rows.append(row)
    time.sleep(2)   # be polite to the free API

summary = pd.DataFrame(monthly_rows)
summary.to_csv(OUT / "monthly_summary.csv", index=False)

# ---------------------------------------------------------------------------
# 5. Headline numbers for the synopsis
# ---------------------------------------------------------------------------
print("\n=== Headlines (working hours 8am-6pm) ===")
for place, g in summary.groupby("place"):
    yr = g[g["month"].str.startswith("2025")]
    print(f"{place:20s} 2025: "
          f"{yr[f'work_hours_wbgt_ge_{WBGT_BANDS[1]}'].sum():5d} work-hours WBGT>={WBGT_BANDS[1]} | "
          f"{yr['days_pm10_over_limit'].sum():3d} days PM10>{PM10_DAY_LIMIT} | "
          f"hottest WBGT {yr['max_wbgt_est_c'].max()} C")
print("\nSaved files in ./data")
