# Database (owner: Neel)

Neel builds the schema here himself. These notes are only the agreed inputs.

## Reading format (agreed with Person 2 and Person 3)

```json
{"device_id":"node-01","time":"2026-11-05T14:00:00+05:30","temp":38.2,"humidity":30,"globe_temp":52.1,"pm25":45,"pm10":120,"uv":9}
```

Replay devices use ids starting with `replay-` (e.g. `replay-dust-01`) so demo data can never be mistaken for real measurements.

## Planned tables

workers, sites, devices, readings, daily_exposure, rules, cases, symptoms, alerts, exports

## Limits to load into `rules` (store as data, not hard-coded)

| Hazard | Warning | Action: book check-up | Source |
|---|---|---|---|
| WBGT, heavy work (hourly average) | 26 °C *(our choice)* | 27.5 °C | ACGIH TLV, used in Jakobsson et al. 2023 |
| WBGT, moderate work | 26.5 °C *(our choice)* | 28 °C | ACGIH TLV |
| Respirable silica estimate, 8-h average | 25 µg/m³ (action level) | 50 µg/m³ | OSHA PEL / NIOSH REL |
| Dust sensor glitch | discard reading > 10,000 µg/m³ | – | NIOSH 2024 saw >1,000,000 spikes |

Silica estimate = 8-h average PM10 × site's silica % from a lab sample (NIOSH 2024 method). The sensor alone cannot detect silica.
