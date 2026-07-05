-- analysis_queries.sql
-- Core analysis queries for the delivery performance dashboard.
-- These map directly to the Power BI visuals in Week 3.

-- 1. Overall on-time delivery rate (headline KPI)
SELECT
    ROUND(100.0 * SUM(CASE WHEN is_late = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    COUNT(*) AS total_shipments
FROM shipments;

-- 2. Delay rate by region (feeds the risk heatmap)
SELECT
    order_region,
    COUNT(*) AS total_shipments,
    SUM(is_late) AS late_shipments,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days
FROM shipments
GROUP BY order_region
ORDER BY late_pct DESC;

-- 3. Delay rate by shipping mode / carrier proxy
SELECT
    shipping_mode,
    COUNT(*) AS total_shipments,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days
FROM shipments
GROUP BY shipping_mode
ORDER BY late_pct DESC;

-- 4. Delay rate by product category
SELECT
    category_name,
    COUNT(*) AS total_shipments,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM shipments
GROUP BY category_name
ORDER BY late_pct DESC
LIMIT 15;

-- 5. Monthly trend of late deliveries (for the trend line visual)
SELECT
    DATE_TRUNC('month', order_date_dateorders) AS order_month,
    COUNT(*) AS total_shipments,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct
FROM shipments
GROUP BY DATE_TRUNC('month', order_date_dateorders)
ORDER BY order_month;

-- 6. Simple risk score per region+shipping_mode combination
-- (Weighted combination of late % and average delay severity —
--  refine this once you've explored the data further)
--
-- DATA NOTE: First Class rows will always show 100% late / risk score 73.0
-- regardless of region. This was investigated (see README Key Findings) and
-- confirmed to be an SLA design issue, not an operational one — every First
-- Class order is scheduled for 1 day but takes 2, with zero variance across
-- all 27,814 orders. When presenting this dashboard, treat First Class as a
-- separate finding ("fix the SLA") rather than mixing it into the same
-- "operational risk" ranking as the other shipping modes.
SELECT
    order_region,
    shipping_mode,
    COUNT(*) AS total_shipments,
    ROUND(100.0 * SUM(is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(
        (100.0 * SUM(is_late) / COUNT(*)) * 0.7 +
        (AVG(delay_days) * 10) * 0.3,
        1
    ) AS risk_score
FROM shipments
GROUP BY order_region, shipping_mode
HAVING COUNT(*) > 30  -- exclude low-volume combos that would skew the score
ORDER BY risk_score DESC;

-- 7. Weather correlation (once weather_log has enough history)
-- Joins on city name — adjust matching logic based on how order_city
-- values compare to your HUB_LOCATIONS keys in 02_weather_pull.py
SELECT
    w.city,
    w.condition,
    COUNT(s.order_id) AS shipments_during_condition,
    ROUND(100.0 * SUM(s.is_late) / COUNT(s.order_id), 1) AS late_pct
FROM weather_log w
JOIN shipments s
    ON s.order_city = w.city
    AND DATE(s.shipping_date_dateorders) = DATE(w.pulled_at_utc)
GROUP BY w.city, w.condition
ORDER BY late_pct DESC;
