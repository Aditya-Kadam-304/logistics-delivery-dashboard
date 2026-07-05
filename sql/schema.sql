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

CREATE INDEX IF NOT EXISTS idx_shipments_region ON shipments(order_region);
CREATE INDEX IF NOT EXISTS idx_shipments_shipping_mode ON shipments(shipping_mode);
CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_log(city, pulled_at_utc);
