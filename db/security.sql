-- Ford Fleet Management Demo - Security Model
-- RBAC (Role-Based Access Control) and RLS (Row-Level Security) implementation

USE ford_fleet;

-- =============================================================================
-- DATABASE ROLES
-- =============================================================================

-- Territory Manager role - can read territory-scoped data
CREATE ROLE IF NOT EXISTS fleet_territory_manager;

-- Regional Manager role - can read region-scoped data (all territories in region)
CREATE ROLE IF NOT EXISTS fleet_regional_manager;

-- Admin role - full read access to all data
CREATE ROLE IF NOT EXISTS fleet_admin;

-- Ingest role - insert-only access for Kafka consumer
CREATE ROLE IF NOT EXISTS fleet_ingest;

-- =============================================================================
-- SECURITY ROLES (for RLS - these are different from database roles)
-- Security roles are used with CURRENT_SECURITY_ROLES() and SECURITY_LISTS_INTERSECT()
-- =============================================================================

-- Territory-level security roles
CREATE SECURITY ROLE IF NOT EXISTS territory_west_1;
CREATE SECURITY ROLE IF NOT EXISTS territory_west_2;
CREATE SECURITY ROLE IF NOT EXISTS territory_east_1;
CREATE SECURITY ROLE IF NOT EXISTS territory_east_2;
CREATE SECURITY ROLE IF NOT EXISTS territory_central_1;
CREATE SECURITY ROLE IF NOT EXISTS territory_central_2;

-- Region-level security roles
CREATE SECURITY ROLE IF NOT EXISTS region_west;
CREATE SECURITY ROLE IF NOT EXISTS region_east;
CREATE SECURITY ROLE IF NOT EXISTS region_central;

-- Admin security role (sees everything)
CREATE SECURITY ROLE IF NOT EXISTS admin_all;

-- =============================================================================
-- DATABASE USERS
-- =============================================================================

-- Territory Manager user (WEST_1 territory)
CREATE USER IF NOT EXISTS 'territory_manager_1'@'%' IDENTIFIED BY 'TerritoryPass123!';

-- Regional Manager user (WEST region - sees all WEST territories)
CREATE USER IF NOT EXISTS 'regional_manager_1'@'%' IDENTIFIED BY 'RegionalPass123!';

-- Demo Admin user (full access)
CREATE USER IF NOT EXISTS 'demo_admin'@'%' IDENTIFIED BY 'AdminPass123!';

-- Ingest user for Kafka consumer
CREATE USER IF NOT EXISTS 'ingest_user'@'%' IDENTIFIED BY 'IngestPass123!';

-- =============================================================================
-- GRANT DATABASE ROLES TO USERS
-- =============================================================================

-- Territory manager gets territory manager role
GRANT fleet_territory_manager TO 'territory_manager_1'@'%';

-- Regional manager gets regional manager role
GRANT fleet_regional_manager TO 'regional_manager_1'@'%';

-- Admin gets admin role
GRANT fleet_admin TO 'demo_admin'@'%';

-- Ingest user gets ingest role
GRANT fleet_ingest TO 'ingest_user'@'%';

-- =============================================================================
-- GRANT SECURITY ROLES TO USERS (for RLS)
-- =============================================================================

-- Territory manager 1 can see WEST_1 territory
GRANT SECURITY ROLE territory_west_1 TO 'territory_manager_1'@'%';

-- Regional manager 1 can see all WEST region data
GRANT SECURITY ROLE region_west TO 'regional_manager_1'@'%';

-- Demo admin can see everything
GRANT SECURITY ROLE admin_all TO 'demo_admin'@'%';
GRANT SECURITY ROLE region_west TO 'demo_admin'@'%';
GRANT SECURITY ROLE region_east TO 'demo_admin'@'%';
GRANT SECURITY ROLE region_central TO 'demo_admin'@'%';

-- =============================================================================
-- GRANT TABLE PRIVILEGES
-- =============================================================================

-- Territory Manager privileges (read-only on most tables)
GRANT SELECT ON ford_fleet.customers TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.regions TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.territories TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.vehicles TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.vehicle_state TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.telemetry_raw TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.anomalies TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.driver_notes TO fleet_territory_manager;
-- Allow updating anomaly acknowledgement
GRANT UPDATE ON ford_fleet.anomalies TO fleet_territory_manager;

-- Regional Manager privileges (same as territory but broader RLS scope)
GRANT SELECT ON ford_fleet.customers TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.regions TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.territories TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.vehicles TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.vehicle_state TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.telemetry_raw TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.anomalies TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.driver_notes TO fleet_regional_manager;
GRANT UPDATE ON ford_fleet.anomalies TO fleet_regional_manager;

-- Admin privileges (full read access)
GRANT SELECT ON ford_fleet.* TO fleet_admin;
GRANT UPDATE ON ford_fleet.anomalies TO fleet_admin;
GRANT INSERT ON ford_fleet.driver_notes TO fleet_admin;

-- Ingest user privileges (insert-only where needed)
GRANT INSERT ON ford_fleet.telemetry_raw TO fleet_ingest;
GRANT INSERT ON ford_fleet.anomalies TO fleet_ingest;
GRANT INSERT, UPDATE ON ford_fleet.vehicle_state TO fleet_ingest;
GRANT SELECT ON ford_fleet.vehicles TO fleet_ingest;

-- =============================================================================
-- ROW-LEVEL SECURITY VIEWS
-- =============================================================================

-- RLS View for telemetry_raw
-- Filters rows based on user's security roles matching the access_roles column
CREATE OR REPLACE VIEW v_telemetry_raw AS
SELECT 
    customer_id,
    vehicle_id,
    ts,
    region_id,
    territory_id,
    lat,
    lon,
    speed,
    engine_temp,
    fuel_pct,
    battery_v,
    odometer,
    dtc_code,
    heading,
    rpm,
    throttle_pct
FROM telemetry_raw
WHERE SECURITY_LISTS_INTERSECT(CURRENT_SECURITY_ROLES(), access_roles);

-- RLS View for vehicles
CREATE OR REPLACE VIEW v_vehicles AS
SELECT 
    vehicle_id,
    customer_id,
    region_id,
    territory_id,
    vin,
    make,
    model,
    year,
    color,
    license_plate,
    driver_name,
    created_at
FROM vehicles
WHERE SECURITY_LISTS_INTERSECT(CURRENT_SECURITY_ROLES(), access_roles);

-- RLS View for anomalies
CREATE OR REPLACE VIEW v_anomalies AS
SELECT 
    anomaly_id,
    vehicle_id,
    customer_id,
    region_id,
    territory_id,
    detected_at,
    anomaly_type,
    severity,
    description,
    metric_value,
    threshold_value,
    acknowledged,
    acknowledged_by,
    acknowledged_at
FROM anomalies
WHERE SECURITY_LISTS_INTERSECT(CURRENT_SECURITY_ROLES(), access_roles);

-- RLS View for driver_notes
CREATE OR REPLACE VIEW v_driver_notes AS
SELECT 
    note_id,
    vehicle_id,
    customer_id,
    driver_id,
    driver_name,
    ts,
    note_text,
    category,
    region_id,
    territory_id
FROM driver_notes
WHERE SECURITY_LISTS_INTERSECT(CURRENT_SECURITY_ROLES(), access_roles);

-- RLS View for vehicle_state (join with vehicles to get access_roles)
CREATE OR REPLACE VIEW v_vehicle_state AS
SELECT 
    vs.vehicle_id,
    vs.last_seen_ts,
    vs.status,
    vs.lat,
    vs.lon,
    vs.speed,
    vs.heading,
    vs.fuel_pct,
    vs.engine_temp,
    vs.battery_v,
    vs.odometer
FROM vehicle_state vs
INNER JOIN vehicles v ON vs.vehicle_id = v.vehicle_id
WHERE SECURITY_LISTS_INTERSECT(CURRENT_SECURITY_ROLES(), v.access_roles);

-- =============================================================================
-- GRANT VIEW ACCESS
-- =============================================================================

GRANT SELECT ON ford_fleet.v_telemetry_raw TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.v_vehicles TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.v_anomalies TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.v_driver_notes TO fleet_territory_manager;
GRANT SELECT ON ford_fleet.v_vehicle_state TO fleet_territory_manager;

GRANT SELECT ON ford_fleet.v_telemetry_raw TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.v_vehicles TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.v_anomalies TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.v_driver_notes TO fleet_regional_manager;
GRANT SELECT ON ford_fleet.v_vehicle_state TO fleet_regional_manager;

GRANT SELECT ON ford_fleet.v_telemetry_raw TO fleet_admin;
GRANT SELECT ON ford_fleet.v_vehicles TO fleet_admin;
GRANT SELECT ON ford_fleet.v_anomalies TO fleet_admin;
GRANT SELECT ON ford_fleet.v_driver_notes TO fleet_admin;
GRANT SELECT ON ford_fleet.v_vehicle_state TO fleet_admin;

-- =============================================================================
-- HELPER FUNCTIONS FOR ACCESS_ROLES MANAGEMENT
-- =============================================================================

-- Helper to format access_roles correctly: ,ROLE_A,ROLE_B,
-- Usage: SELECT format_access_roles('TERRITORY_WEST_1', 'REGION_WEST');
DELIMITER //

CREATE OR REPLACE FUNCTION format_access_roles(roles_csv TEXT) 
RETURNS VARBINARY(256) AS
BEGIN
    -- Input: comma-separated roles like 'TERRITORY_WEST_1,REGION_WEST'
    -- Output: formatted as ',TERRITORY_WEST_1,REGION_WEST,'
    IF roles_csv IS NULL OR roles_csv = '' THEN
        RETURN CAST(',' AS VARBINARY(256));
    END IF;
    RETURN CAST(CONCAT(',', roles_csv, ',') AS VARBINARY(256));
END //

DELIMITER ;

-- =============================================================================
-- EXAMPLE: Setting ACCESS_ROLES for demo rows
-- =============================================================================

-- Update vehicles with proper access_roles based on their territory and region
-- This should be run after seed data is inserted

-- Example update pattern (run after seed.sql):
-- UPDATE vehicles 
-- SET access_roles = format_access_roles(CONCAT('TERRITORY_', territory_id, ',REGION_', region_id, ',ADMIN_ALL'))
-- WHERE access_roles = ',';

-- UPDATE telemetry_raw 
-- SET access_roles = format_access_roles(CONCAT('TERRITORY_', territory_id, ',REGION_', region_id, ',ADMIN_ALL'))
-- WHERE access_roles = ',';

-- UPDATE anomalies 
-- SET access_roles = format_access_roles(CONCAT('TERRITORY_', territory_id, ',REGION_', region_id, ',ADMIN_ALL'))
-- WHERE access_roles = ',';

