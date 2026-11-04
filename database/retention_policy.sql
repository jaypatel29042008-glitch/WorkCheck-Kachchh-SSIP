-- ============================================================================
-- OCCUPATIONAL HEALTH DATABASE RETENTION & TIERING POLICY (PS000109)
-- ============================================================================
-- STORAGE BALANCING STRATEGY:
-- 1. Tier 1 (Hot NVMe): Raw Telemetry (`readings`)
--    - Retention Window: 30 days rolling (expandable to 90 days).
--    - Purpose: Live real-time lamp triggers, sensor calibration, dispute resolution.
--    - Ingestion Volume:
--      * 50 Site Nodes @ 1 reading / 5 mins = 14,400 rows/day (~2.5 MB/day uncompressed).
--      * 1,000 Dust Badges @ 1 reading / 1 min (8hr shift) = 480,000 rows/day (~40 MB/day).
--      * 30-day Hot Storage footprint: ~1.2 GB (compact, fast indexed queries).
--
-- 2. Tier 2 (Warm / Analytical): Summarized Rollup (`daily_exposure`)
--    - Retention Window: PERMANENT (Immutable longitudinal occupational health record).
--    - Ingestion Volume: 1,000 rows/day (~120 KB/day).
--    - Annual footprint: ~43 MB/year for 1,000 workers!
--    - Storage reduction factor: 99.7% reduction compared to raw storage.
--
-- 3. Tier 3 (Cold Archive): S3 / Glacier Parquet Export
--    - Monthly exports of raw telemetry compressed to Apache Parquet for academic research.
-- ============================================================================

-- Daily Automated Aggregation Procedure (Executed at 23:59:00 UTC / IST 05:29:00)
-- PostgreSQL Implementation:
/*
CREATE OR REPLACE FUNCTION run_nightly_worker_exposure_rollup(target_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_exposure (
        worker_id, site_id, shift_date, shift_duration_hours,
        avg_pm2_5_ug_m3, peak_pm2_5_ug_m3, avg_pm10_ug_m3,
        cumulative_dust_dose_mg_m3_hr, avg_wbgt_c, max_wbgt_c,
        hours_above_wbgt_28, hours_above_wbgt_30,
        flag_over_exposure, flag_reason
    )
    SELECT 
        r.worker_id,
        r.site_id,
        target_date,
        ROUND((EXTRACT(EPOCH FROM (MAX(r.recorded_at) - MIN(r.recorded_at))) / 3600.0)::numeric, 2) AS shift_duration,
        ROUND(AVG(r.pm2_5_ug_m3), 2),
        ROUND(MAX(r.pm2_5_ug_m3), 2),
        ROUND(AVG(r.pm10_0_ug_m3), 2),
        -- Cumulative dose = (Avg PM2.5 mg/m3) * hours
        ROUND((AVG(r.pm2_5_ug_m3) / 1000.0 * (EXTRACT(EPOCH FROM (MAX(r.recorded_at) - MIN(r.recorded_at))) / 3600.0))::numeric, 3),
        ROUND(AVG(r.calculated_wbgt_c), 2),
        ROUND(MAX(r.calculated_wbgt_c), 2),
        -- Count readings above thresholds (assuming 5-min intervals = 1/12 hour per reading)
        ROUND((COUNT(CASE WHEN r.calculated_wbgt_c >= 28.0 THEN 1 END) * 5.0 / 60.0)::numeric, 2),
        ROUND((COUNT(CASE WHEN r.calculated_wbgt_c >= 30.0 THEN 1 END) * 5.0 / 60.0)::numeric, 2),
        CASE 
            WHEN MAX(r.calculated_wbgt_c) >= 31.0 OR AVG(r.pm2_5_ug_m3) >= 150.0 THEN TRUE 
            ELSE FALSE 
        END,
        CASE 
            WHEN MAX(r.calculated_wbgt_c) >= 31.0 THEN 'Exceeded 31C WBGT Emergency Heat Limit'
            WHEN AVG(r.pm2_5_ug_m3) >= 150.0 THEN 'Exceeded Respirable PM2.5 Action Level'
            ELSE NULL 
        END
    FROM readings r
    WHERE r.worker_id IS NOT NULL 
      AND r.recorded_at::date = target_date
    GROUP BY r.worker_id, r.site_id
    ON CONFLICT (worker_id, shift_date) DO UPDATE 
    SET avg_wbgt_c = EXCLUDED.avg_wbgt_c,
        max_wbgt_c = EXCLUDED.max_wbgt_c,
        hours_above_wbgt_30 = EXCLUDED.hours_above_wbgt_30,
        flag_over_exposure = EXCLUDED.flag_over_exposure;
END;
$$ LANGUAGE plpgsql;
*/

-- 30-Day Purge Trigger for Raw Telemetry (SQLite & PostgreSQL Compatible)
-- Keeps high-frequency readings table light, fast, and cache-friendly.
DELETE FROM readings 
WHERE recorded_at < datetime('now', '-30 days');

-- Vacuum to reclaim disk space after monthly purge
-- VACUUM;
