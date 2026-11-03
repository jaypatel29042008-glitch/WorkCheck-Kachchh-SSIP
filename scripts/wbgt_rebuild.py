"""
WBGT rebuilt from the research papers - every method, step by step.

WBGT (Wet Bulb Globe Temperature) = one number for heat stress on the body.
It mixes 3 thermometers:
    Tnwb  natural wet bulb   - a wet wick in open air (shows how well sweat can cool you)
    Tg    black globe        - a black ball in the sun (shows radiant heat from sun / hot surfaces)
    Ta    air temperature    - a normal thermometer in shade

METHODS (who used what)
  A. ISO 7243 / ACGIH formula, measured with a heat-stress meter
       -> Tamil Nadu salt pans (Jakobsson et al. 2023, QuesTemp 34 meter)
       -> Indian steel / foundry studies
  B. Bernard (1999): estimate the wet bulb from air temp + humidity + wind (+ globe)
       -> our site node: we measure Ta, RH, Tg (150 mm globe), wind, but have no wet wick
       -> with Tg = Ta it becomes the "shade / indoor" method recommended by
          Lemke & Kjellstrom (2012)
  C. Liljegren (2008): full physics model from weather data, works in the sun
       -> recommended outdoor method (Lemke & Kjellstrom 2012), used by ClimateCHIP
  D. ABOM / ACSM simple formula: temperature + humidity only
       -> quick screening only (no sun, no wind)

Run:
    pip install numpy pandas matplotlib thermofeel pythermalcomfort
    python wbgt_rebuild.py                     # checks + worked example + method chart
    python wbgt_rebuild.py data/hourly_mundra_port.csv
        # applies every weather method to an hourly Open-Meteo file
        # (needs the extra columns added in get_kutch_data.py - see bottom)
"""

import math
import sys

import numpy as np
import pandas as pd

# Safe limits (ACGIH TLV, acclimatised worker, continuous work) - from the TN study
TLV = {"moderate": 28.0, "heavy": 27.5}


# ---------------------------------------------------------------------------
# Step 1: humidity helpers
# ---------------------------------------------------------------------------
def sat_vapour_pressure(t_c):
    """Saturation vapour pressure (hPa): the most water air can hold at t_c."""
    return 6.106 * math.exp(17.27 * t_c / (237.3 + t_c))


def dew_point(ta, rh):
    """Dew point (C): temperature where the air would start to form dew (Magnus)."""
    g = math.log(rh / 100) + 17.27 * ta / (237.3 + ta)
    return 237.3 * g / (17.27 - g)


def psychrometric_wet_bulb(ta, td):
    """
    Psychrometric wet bulb Tpwb (C) - a wet thermometer with forced airflow.
    Solves Bernard / Lemke-Kjellstrom Eq. 9 by bisection:
        1556*ed - 1.484*ed*Tw - 1556*ew + 1.484*ew*Tw + 1010*(Ta - Tw) = 0
    ed = vapour pressure at dew point, ew = saturation pressure at Tw.
    """
    ed = sat_vapour_pressure(td)

    def f(tw):
        ew = sat_vapour_pressure(tw)
        return 1556 * ed - 1.484 * ed * tw - 1556 * ew + 1.484 * ew * tw + 1010 * (ta - tw)

    lo, hi = td, ta            # wet bulb always lies between dew point and air temp
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# Method A: ISO 7243 formula (when you HAVE all three thermometers)
# ---------------------------------------------------------------------------
def wbgt_iso(tnwb, tg, ta=None, sun=True):
    """Outdoor (sun): 0.7*Tnwb + 0.2*Tg + 0.1*Ta.  Indoor/shade: 0.7*Tnwb + 0.3*Tg."""
    if sun:
        return 0.7 * tnwb + 0.2 * tg + 0.1 * ta
    return 0.7 * tnwb + 0.3 * tg


# ---------------------------------------------------------------------------
# Method B: Bernard - estimate the natural wet bulb, then use ISO formula
# ---------------------------------------------------------------------------
def natural_wet_bulb_bernard(ta, rh, tg, v):
    """
    Natural wet bulb Tnwb (C) from Lemke & Kjellstrom 2012, Eq. 6 (Bernard 1999).
    v = wind speed at the worker (m/s); clamped to 0.3 m/s minimum.
    """
    v = max(v, 0.3)
    tpwb = psychrometric_wet_bulb(ta, dew_point(ta, rh))
    if tg - ta >= 4:                                   # strong radiant heat
        return tpwb + 0.25 * (tg - ta) + 0.1 / v ** 1.1 - 0.2
    if v > 3:                                          # windy, little radiation
        return tpwb
    return ta - (0.96 + 0.069 * math.log10(v)) * (ta - tpwb)


def wbgt_site_node(ta, rh, tg, v=1.0):
    """
    What OUR device does: measured Ta, RH, globe Tg (150 mm black globe), wind v.
    Tnwb estimated with Bernard, then ISO outdoor formula.
    """
    tnwb = natural_wet_bulb_bernard(ta, rh, tg, v)
    return wbgt_iso(tnwb, tg, ta, sun=True)


def wbgt_shade_bernard(ta, rh, v=1.0):
    """Weather-only, shade/indoor: Tg = Ta (no radiant source). Lemke & Kjellstrom."""
    tnwb = natural_wet_bulb_bernard(ta, rh, ta, v)
    return wbgt_iso(tnwb, ta, sun=False)


# ---------------------------------------------------------------------------
# Method C: Liljegren (sun) - full heat-balance physics; use the tested library
# ---------------------------------------------------------------------------
def wbgt_sun_liljegren(ta, rh, wind10, solar, direct_frac, cos_zenith, pressure=1005.0):
    """
    Outdoor WBGT in sun from weather data (thermofeel's implementation of
    Liljegren et al. 2008). solar = W/m2 on flat ground, direct_frac 0-1,
    cos_zenith = height of the sun (1 = overhead, 0 = horizon).
    Wind is at 10 m (weather-model height); library scales it to 2 m.
    """
    import thermofeel as tf
    k = tf.calculate_wbgt_liljegren(
        np.atleast_1d(ta + 273.15), np.atleast_1d(rh), np.atleast_1d(pressure),
        np.atleast_1d(wind10), np.atleast_1d(solar), np.atleast_1d(direct_frac),
        np.atleast_1d(max(cos_zenith, 0.01)))
    return float(k[0]) - 273.15


# ---------------------------------------------------------------------------
# Method D: ABOM simple (temp + humidity only)
# ---------------------------------------------------------------------------
def wbgt_abom(ta, rh):
    e = rh / 100 * 6.105 * math.exp(17.27 * ta / (237.7 + ta))
    return 0.567 * ta + 0.393 * e + 3.94


# ---------------------------------------------------------------------------
# Checks: my hand-written code vs. published / library values
# ---------------------------------------------------------------------------
def run_checks():
    import thermofeel as tf
    from pythermalcomfort.models import wbgt as ptc_wbgt

    print("=== CHECKS (my code vs. independent code) ===")
    rows = []
    for ta, rh in [(30, 70), (35, 50), (40, 30), (45, 20)]:
        mine = wbgt_abom(ta, rh)
        lib = float(tf.calculate_wbgt_simple(np.array([ta + 273.15]), np.array([rh]))[0]) - 273.15
        rows.append(("ABOM simple", f"Ta={ta} RH={rh}", mine, lib))
    for tnwb, tg, ta in [(25, 50, 35), (28, 45, 38)]:
        mine = wbgt_iso(tnwb, tg, ta, sun=True)
        lib = ptc_wbgt(twb=tnwb, tg=tg, tdb=ta, with_solar_load=True).wbgt
        rows.append(("ISO 7243 sun", f"Tnwb={tnwb} Tg={tg} Ta={ta}", mine, lib))
    # textbook check: 20 C, 50% RH -> wet bulb about 13.7 C
    tw = psychrometric_wet_bulb(20, dew_point(20, 50))
    rows.append(("Wet bulb", "Ta=20 RH=50 (expect ~13.7)", tw, 13.7))
    for name, case, a, b in rows:
        print(f"{name:13s} {case:28s} mine={a:6.2f}  reference={b:6.2f}  diff={a-b:+.2f}")


# ---------------------------------------------------------------------------
# Worked example: one hot afternoon (EXAMPLE INPUTS, not measured data)
# ---------------------------------------------------------------------------
def worked_example():
    ta, rh, tg, v = 42.0, 25.0, 58.0, 1.5     # example inputs only
    print("\n=== WORKED EXAMPLE (example inputs: Ta 42 C, RH 25 %, globe 58 C, wind 1.5 m/s) ===")
    td = dew_point(ta, rh)
    tpwb = psychrometric_wet_bulb(ta, td)
    tnwb = natural_wet_bulb_bernard(ta, rh, tg, v)
    print(f"1. dew point              Td   = {td:5.1f} C")
    print(f"2. psychrometric wet bulb Tpwb = {tpwb:5.1f} C")
    print(f"3. natural wet bulb       Tnwb = {tpwb:.1f} + 0.25*({tg}-{ta}) + 0.1/{v}^1.1 - 0.2 = {tnwb:5.1f} C")
    w = wbgt_iso(tnwb, tg, ta)
    print(f"4. WBGT = 0.7*{tnwb:.1f} + 0.2*{tg} + 0.1*{ta} = {w:5.1f} C")
    for job, lim in TLV.items():
        print(f"   {job:8s} work limit {lim} C -> {'OVER' if w > lim else 'ok'} by {w - lim:+.1f} C")
    print("\nSame air, other methods:")
    print(f"   shade (Bernard, Tg=Ta)       {wbgt_shade_bernard(ta, rh, v):5.1f} C")
    print(f"   sun (Liljegren, 900 W/m2)    {wbgt_sun_liljegren(ta, rh, 3.0, 900, 0.8, 0.9):5.1f} C")
    print(f"   ABOM simple                  {wbgt_abom(ta, rh):5.1f} C")


# ---------------------------------------------------------------------------
# Chart: how the methods differ (formula behaviour, not field data)
# ---------------------------------------------------------------------------
def method_chart(path="wbgt_methods.png", rh=30):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    temps = np.arange(28, 47, 1.0)
    shade = [wbgt_shade_bernard(t, rh, 1.0) for t in temps]
    sun = [wbgt_sun_liljegren(t, rh, 3.0, 900, 0.8, 0.9) for t in temps]
    simple = [wbgt_abom(t, rh) for t in temps]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.plot(temps, sun, color="#c2410c", lw=2.2, label="In sun - Liljegren (weather data)")
    ax.plot(temps, simple, color="#6b7280", lw=1.8, ls="--", label="Simple ABOM (temp + humidity)")
    ax.plot(temps, shade, color="#2563eb", lw=2.2, label="In shade - Bernard (weather data)")
    ax.axhline(TLV["heavy"], color="#111827", lw=1, ls=":")
    ax.text(46, TLV["heavy"] - 0.9, "Safe limit, heavy work (27.5 °C)", fontsize=9, ha="right")
    ax.set_xlabel("Air temperature (°C)")
    ax.set_ylabel("WBGT (°C)")
    ax.set_title(f"Same air, different WBGT: sun vs shade (RH {rh}%, wind ~1 m/s)", fontsize=11)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.01, 0.01, "Formula comparison with example inputs - not field measurements.",
             fontsize=7, color="#6b7280")
    fig.tight_layout()
    fig.savefig(path)
    print(f"\nSaved chart -> {path}")


# ---------------------------------------------------------------------------
# Apply to a real hourly Open-Meteo file
# ---------------------------------------------------------------------------
def cos_solar_zenith(ts_local, lat, lon, tz_hours=5.5):
    """Height of the sun (NOAA simplified). ts_local = naive local time (IST)."""
    doy = ts_local.timetuple().tm_yday
    hour = ts_local.hour + ts_local.minute / 60
    g = 2 * math.pi / 365 * (doy - 1 + (hour - 12) / 24)
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g)
            - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    solar_min = hour * 60 + eqt + 4 * lon - 60 * tz_hours
    ha = math.radians(solar_min / 4 - 180)
    la = math.radians(lat)
    return math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)


def apply_to_file(csv_path, lat=None, lon=None):
    df = pd.read_csv(csv_path, parse_dates=["time"])
    need = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "shortwave_radiation"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        sys.exit(f"Missing columns {miss}. Re-run get_kutch_data.py with the extra variables.")
    if lat is None:
        lat, lon = float(df["latitude"].iloc[0]), float(df["longitude"].iloc[0])

    out = []
    for r in df.itertuples():
        ta, rh = r.temperature_2m, r.relative_humidity_2m
        if pd.isna(ta) or pd.isna(rh):
            out.append((np.nan, np.nan, np.nan))
            continue
        wind10 = r.wind_speed_10m / 3.6               # Open-Meteo gives km/h
        # Open-Meteo radiation = average over the PREVIOUS hour -> use mid-hour sun position
        cz = cos_solar_zenith(r.time - pd.Timedelta(minutes=30), lat, lon)
        sw = r.shortwave_radiation
        fdir = (getattr(r, "direct_radiation", sw * 0.7) / sw) if sw > 1 else 0.0
        p = getattr(r, "surface_pressure", 1005.0)
        sun = wbgt_sun_liljegren(ta, rh, wind10, sw if cz > 0 else 0.0,
                                 min(max(fdir, 0), 1), cz, p)
        shade = wbgt_shade_bernard(ta, rh, max(wind10 * 0.67, 0.3))  # rough 10 m -> 2 m
        out.append((sun, shade, wbgt_abom(ta, rh)))
    df[["wbgt_sun", "wbgt_shade", "wbgt_abom"]] = out

    work = df[df["time"].dt.hour.between(8, 17)]
    print(f"\n=== {csv_path}: working hours 8 am - 6 pm ===")
    for col in ["wbgt_sun", "wbgt_shade", "wbgt_abom"]:
        print(f"{col:11s} hours over heavy-work limit 27.5 C: {(work[col] > 27.5).sum():6d}"
              f" | max {work[col].max():.1f} C")
    outp = csv_path.replace(".csv", "_wbgt_methods.csv")
    df.to_csv(outp, index=False)
    print(f"Saved -> {outp}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        apply_to_file(sys.argv[1])
    else:
        run_checks()
        worked_example()
        method_chart()

# apply_to_file needs the hourly CSVs from scripts/get_kutch_data.py
# (it already downloads direct_radiation + surface_pressure and saves lat/lon).
