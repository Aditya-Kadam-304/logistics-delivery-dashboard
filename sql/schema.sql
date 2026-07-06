-- schema.sql
-- Run this once against your PostgreSQL database before loading data.

CREATE TABLE IF NOT EXISTS shipments (
    order_id INTEGER,
    order_date_dateorders TIMESTAMP,
    shipping_date_dateorders TIMESTAMP,
    order_region VARCHAR(100),
    order_country VARCHAR(100),
    order_city VARCHAR(100),
    market VARCHAR(50),
    shipping_mode VARCHAR(50),
    late_delivery_risk INTEGER,
    days_for_shipping_real INTEGER,
    days_for_shipment_scheduled INTEGER,
    is_late INTEGER,
    delay_days INTEGER,
    order_item_quantity INTEGER,
    sales NUMERIC(10, 2),
    category_name VARCHAR(100),
    customer_segment VARCHAR(50),
    department_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS weather_log (
    pulled_at_utc TIMESTAMP,
    city VARCHAR(100),
    temp_c NUMERIC(5, 2),
    condition VARCHAR(50),
    description VARCHAR(150),
    wind_speed_ms NUMERIC(5, 2),
    humidity_pct INTEGER
);

-- Real historical weather, matched to actual shipment dates — this is what
-- the weather-to-delivery correlation analysis actually uses. weather_log
-- above only captures "today," and is kept purely as a live-automation demo.
CREATE TABLE IF NOT EXISTS historical_weather (
    order_city VARCHAR(100),
    date DATE,
    precipitation_mm NUMERIC(6, 2),
    temp_mean_c NUMERIC(5, 2),
    weather_code INTEGER,
    weather_condition VARCHAR(30)
);

CREATE INDEX IF NOT EXISTS idx_shipments_region ON shipments(order_region);
CREATE INDEX IF NOT EXISTS idx_shipments_shipping_mode ON shipments(shipping_mode);
CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_log(city, pulled_at_utc);
CREATE INDEX IF NOT EXISTS idx_historical_weather_city_date ON historical_weather(order_city, date);
