-- Ford Fleet Management Demo - Database Schema
-- SingleStore DDL for rowstore (transactional) and columnstore (analytics) tables

-- =============================================================================
-- DATABASE CREATION
-- =============================================================================
CREATE DATABASE IF NOT EXISTS ford_fleet;
USE ford_fleet;

-- =============================================================================
-- ROWSTORE TABLES (Transactional Entities)
-- =============================================================================

-- Customers table - each customer has their own Kafka topic
CREATE ROWSTORE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    kafka_topic_name VARCHAR(128) NOT NULL,
    created_at DATETIME(6) DEFAULT NOW(6),
    PRIMARY KEY (customer_id),
    SHARD KEY (customer_id)
);

-- Users table - application users with role assignments
CREATE ROWSTORE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) NOT NULL,
    username VARCHAR(128) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(64) NOT NULL,
    region_id VARCHAR(32),
    territory_id VARCHAR(32),
    is_active TINYINT DEFAULT 1,
    created_at DATETIME(6) DEFAULT NOW(6),
    PRIMARY KEY (user_id),
    SHARD KEY (user_id)
);

-- Regions table - geographic regions
CREATE ROWSTORE TABLE IF NOT EXISTS regions (
    region_id VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    created_at DATETIME(6) DEFAULT NOW(6),
    PRIMARY KEY (region_id),
    SHARD KEY (region_id)
);

-- Territories table - subdivisions within regions
CREATE ROWSTORE TABLE IF NOT EXISTS territories (
    territory_id VARCHAR(32) NOT NULL,
    region_id VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    created_at DATETIME(6) DEFAULT NOW(6),
    PRIMARY KEY (territory_id),
    SHARD KEY (territory_id)
);

-- Vehicles table - fleet vehicle metadata
CREATE ROWSTORE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    region_id VARCHAR(32) NOT NULL,
    territory_id VARCHAR(32) NOT NULL,
    vin VARCHAR(17) NOT NULL,
    make VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(32),
    license_plate VARCHAR(16),
    driver_name VARCHAR(128),
    access_roles VARBINARY(256) NOT NULL DEFAULT ',',
    created_at DATETIME(6) DEFAULT NOW(6),
    PRIMARY KEY (vehicle_id),
    SHARD KEY (vehicle_id)
);

-- Vehicle state table - latest status per vehicle (upsert target)
CREATE ROWSTORE TABLE IF NOT EXISTS vehicle_state (
    vehicle_id VARCHAR(64) NOT NULL,
    last_seen_ts DATETIME(6) NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    lat DECIMAL(10, 7),
    lon DECIMAL(10, 7),
    speed DECIMAL(6, 2),
    heading DECIMAL(5, 2),
    fuel_pct DECIMAL(5, 2),
    engine_temp DECIMAL(6, 2),
    battery_v DECIMAL(5, 2),
    odometer INT,
    PRIMARY KEY (vehicle_id),
    SHARD KEY (vehicle_id)
);

-- Anomalies table - detected anomalies with acknowledgement state
CREATE ROWSTORE TABLE IF NOT EXISTS anomalies (
    anomaly_id VARCHAR(64) NOT NULL,
    vehicle_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    region_id VARCHAR(32) NOT NULL,
    territory_id VARCHAR(32) NOT NULL,
    detected_at DATETIME(6) NOT NULL,
    anomaly_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    description TEXT,
    metric_value DECIMAL(10, 2),
    threshold_value DECIMAL(10, 2),
    acknowledged TINYINT DEFAULT 0,
    acknowledged_by VARCHAR(64),
    acknowledged_at DATETIME(6),
    access_roles VARBINARY(256) NOT NULL DEFAULT ',',
    PRIMARY KEY (anomaly_id),
    SHARD KEY (anomaly_id)
);

-- =============================================================================
-- COLUMNSTORE TABLES (Analytics)
-- =============================================================================

-- Telemetry raw table - shared ingest target for all customer Kafka topics
CREATE TABLE IF NOT EXISTS telemetry_raw (
    customer_id VARCHAR(64) NOT NULL,
    vehicle_id VARCHAR(64) NOT NULL,
    ts DATETIME(6) NOT NULL,
    region_id VARCHAR(32) NOT NULL,
    territory_id VARCHAR(32) NOT NULL,
    lat DECIMAL(10, 7),
    lon DECIMAL(10, 7),
    speed DECIMAL(6, 2),
    engine_temp DECIMAL(6, 2),
    fuel_pct DECIMAL(5, 2),
    battery_v DECIMAL(5, 2),
    odometer INT,
    dtc_code VARCHAR(16),
    heading DECIMAL(5, 2),
    rpm INT,
    throttle_pct DECIMAL(5, 2),
    access_roles VARBINARY(256) NOT NULL DEFAULT ',',
    SHARD KEY (vehicle_id),
    SORT KEY (ts)
);

-- Driver notes table - free text notes for AI summarization
CREATE TABLE IF NOT EXISTS driver_notes (
    note_id VARCHAR(64) NOT NULL,
    vehicle_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    driver_id VARCHAR(64),
    driver_name VARCHAR(128),
    ts DATETIME(6) NOT NULL,
    note_text TEXT NOT NULL,
    category VARCHAR(64),
    region_id VARCHAR(32) NOT NULL,
    territory_id VARCHAR(32) NOT NULL,
    access_roles VARBINARY(256) NOT NULL DEFAULT ',',
    SHARD KEY (vehicle_id),
    SORT KEY (ts)
);

