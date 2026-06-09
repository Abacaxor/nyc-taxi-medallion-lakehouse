CREATE DATABASE IF NOT EXISTS taxi_dw;
USE taxi_dw;

CREATE TABLE IF NOT EXISTS taxi_zones (
    location_id INT PRIMARY KEY,
    borough VARCHAR(80) NOT NULL,
    zone VARCHAR(120) NOT NULL,
    service_zone VARCHAR(80) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS yellow_taxi_trips_raw (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendorid INT NULL,
    tpep_pickup_datetime DATETIME NULL,
    tpep_dropoff_datetime DATETIME NULL,
    passenger_count INT NULL,
    trip_distance DECIMAL(12,4) NULL,
    ratecodeid INT NULL,
    store_and_fwd_flag VARCHAR(10) NULL,
    pulocationid INT NULL,
    dolocationid INT NULL,
    payment_type INT NULL,
    fare_amount DECIMAL(12,2) NULL,
    extra DECIMAL(12,2) NULL,
    mta_tax DECIMAL(12,2) NULL,
    tip_amount DECIMAL(12,2) NULL,
    tolls_amount DECIMAL(12,2) NULL,
    improvement_surcharge DECIMAL(12,2) NULL,
    total_amount DECIMAL(12,2) NULL,
    congestion_surcharge DECIMAL(12,2) NULL,
    airport_fee DECIMAL(12,2) NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pickup_datetime (tpep_pickup_datetime),
    INDEX idx_pickup_location (pulocationid)
);

CREATE TABLE IF NOT EXISTS load_audit (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(120) NOT NULL,
    rows_loaded BIGINT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
