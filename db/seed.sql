-- Ford Fleet Management Demo - Seed Data
-- Demo data for customers, vehicles, users, and initial states

USE ford_fleet;

-- =============================================================================
-- CUSTOMERS
-- =============================================================================

INSERT INTO customers (customer_id, name, kafka_topic_name) VALUES
('customer_a', 'Acme Logistics', 'customer_a_telemetry'),
('customer_b', 'BlueStar Transport', 'customer_b_telemetry');

-- =============================================================================
-- REGIONS
-- =============================================================================

INSERT INTO regions (region_id, name) VALUES
('WEST', 'Western Region'),
('EAST', 'Eastern Region'),
('CENTRAL', 'Central Region');

-- =============================================================================
-- TERRITORIES
-- =============================================================================

INSERT INTO territories (territory_id, region_id, name) VALUES
('WEST_1', 'WEST', 'Pacific Northwest'),
('WEST_2', 'WEST', 'Southwest'),
('EAST_1', 'EAST', 'Northeast'),
('EAST_2', 'EAST', 'Southeast'),
('CENTRAL_1', 'CENTRAL', 'Great Lakes'),
('CENTRAL_2', 'CENTRAL', 'Midwest');

-- =============================================================================
-- APPLICATION USERS
-- =============================================================================

-- Password hashes are bcrypt hashes of the passwords
-- territory_manager_1 / territory123
-- regional_manager_1 / regional123
-- demo_admin / admin123

INSERT INTO users (user_id, username, password_hash, email, role, region_id, territory_id) VALUES
('user_tm1', 'territory_manager_1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4q4N.ZJJn3h3YqHe', 'tm1@ford-demo.com', 'territory_manager', 'WEST', 'WEST_1'),
('user_tm2', 'territory_manager_2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4q4N.ZJJn3h3YqHe', 'tm2@ford-demo.com', 'territory_manager', 'EAST', 'EAST_1'),
('user_rm1', 'regional_manager_1', '$2b$12$8K1p.a1s5x5Q3z5x5Q3z5e5Q3z5x5Q3z5x5Q3z5x5Q3z5x5Q3z5x5e', 'rm1@ford-demo.com', 'regional_manager', 'WEST', NULL),
('user_rm2', 'regional_manager_2', '$2b$12$8K1p.a1s5x5Q3z5x5Q3z5e5Q3z5x5Q3z5x5Q3z5x5Q3z5x5Q3z5x5e', 'rm2@ford-demo.com', 'regional_manager', 'EAST', NULL),
('user_admin', 'demo_admin', '$2b$12$N9qo8uLOickgx2ZMRZoMy.Mrq4H7hKLCzMqTzLqPHFVN5zFVz0xO.', 'admin@ford-demo.com', 'admin', NULL, NULL);

-- =============================================================================
-- VEHICLES - 200+ vehicles across regions and territories
-- =============================================================================

-- Customer A - Acme Logistics (100 vehicles)
-- WEST Region (40 vehicles)
INSERT INTO vehicles (vehicle_id, customer_id, region_id, territory_id, vin, make, model, year, color, license_plate, driver_name, access_roles) VALUES
('v_a_w1_001', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00001', 'Ford', 'F-150', 2023, 'Oxford White', 'WA-001', 'John Smith', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_002', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00002', 'Ford', 'F-150', 2023, 'Agate Black', 'WA-002', 'Sarah Johnson', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_003', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00003', 'Ford', 'Transit', 2022, 'Blue Jeans', 'WA-003', 'Mike Davis', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_004', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00004', 'Ford', 'E-Transit', 2024, 'Oxford White', 'WA-004', 'Emily Chen', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_005', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00005', 'Ford', 'F-250', 2023, 'Iconic Silver', 'WA-005', 'Robert Wilson', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_006', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00006', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'WA-006', 'Lisa Anderson', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_007', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00007', 'Ford', 'Transit Connect', 2023, 'Oxford White', 'WA-007', 'David Martinez', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_008', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00008', 'Ford', 'F-350', 2022, 'Race Red', 'WA-008', 'Jennifer Brown', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_009', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00009', 'Ford', 'Ranger', 2024, 'Cactus Grey', 'WA-009', 'Chris Taylor', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_010', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00010', 'Ford', 'F-150', 2023, 'Carbonized Grey', 'WA-010', 'Amanda White', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_011', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00011', 'Ford', 'Transit', 2023, 'Oxford White', 'WA-011', 'Kevin Lee', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_012', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00012', 'Ford', 'E-Transit', 2024, 'Agate Black', 'WA-012', 'Rachel Green', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_013', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00013', 'Ford', 'F-250', 2022, 'Oxford White', 'WA-013', 'Tom Harris', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_014', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00014', 'Ford', 'F-150', 2024, 'Atlas Blue', 'WA-014', 'Nicole Clark', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_015', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00015', 'Ford', 'Transit', 2023, 'Blue Jeans', 'WA-015', 'Steve Rodriguez', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_016', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00016', 'Ford', 'F-350', 2023, 'Oxford White', 'WA-016', 'Maria Garcia', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_017', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00017', 'Ford', 'F-150 Lightning', 2024, 'Iced Blue Silver', 'WA-017', 'Jason Kim', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_018', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00018', 'Ford', 'Ranger', 2023, 'Oxford White', 'WA-018', 'Laura Thompson', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_019', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00019', 'Ford', 'Transit Connect', 2024, 'Agate Black', 'WA-019', 'Brian Moore', ',territory_west_1,region_west,admin_all,'),
('v_a_w1_020', 'customer_a', 'WEST', 'WEST_1', '1FTFW1E50MFA00020', 'Ford', 'F-250', 2024, 'Carbonized Grey', 'WA-020', 'Samantha Young', ',territory_west_1,region_west,admin_all,'),
('v_a_w2_001', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00021', 'Ford', 'F-150', 2023, 'Oxford White', 'AZ-001', 'Carlos Hernandez', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_002', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00022', 'Ford', 'Transit', 2023, 'Race Red', 'AZ-002', 'Michelle Scott', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_003', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00023', 'Ford', 'F-250', 2022, 'Agate Black', 'AZ-003', 'Andrew King', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_004', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00024', 'Ford', 'E-Transit', 2024, 'Oxford White', 'AZ-004', 'Jessica Wright', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_005', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00025', 'Ford', 'F-350', 2023, 'Iconic Silver', 'AZ-005', 'Daniel Lopez', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_006', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00026', 'Ford', 'F-150', 2024, 'Area 51', 'AZ-006', 'Stephanie Hill', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_007', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00027', 'Ford', 'Transit', 2022, 'Oxford White', 'AZ-007', 'Ryan Adams', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_008', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00028', 'Ford', 'Ranger', 2023, 'Cyber Orange', 'AZ-008', 'Katherine Baker', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_009', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00029', 'Ford', 'F-150 Lightning', 2024, 'Oxford White', 'AZ-009', 'Eric Nelson', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_010', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00030', 'Ford', 'Transit Connect', 2023, 'Blue Jeans', 'AZ-010', 'Amy Carter', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_011', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00031', 'Ford', 'F-250', 2024, 'Oxford White', 'NV-001', 'Mark Mitchell', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_012', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00032', 'Ford', 'F-150', 2023, 'Agate Black', 'NV-002', 'Susan Perez', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_013', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00033', 'Ford', 'E-Transit', 2024, 'Iconic Silver', 'NV-003', 'Timothy Roberts', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_014', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00034', 'Ford', 'Transit', 2023, 'Oxford White', 'NV-004', 'Diana Turner', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_015', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00035', 'Ford', 'F-350', 2022, 'Race Red', 'NV-005', 'George Phillips', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_016', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00036', 'Ford', 'Ranger', 2024, 'Carbonized Grey', 'NV-006', 'Patricia Campbell', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_017', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00037', 'Ford', 'F-150', 2023, 'Oxford White', 'NV-007', 'Joseph Parker', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_018', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00038', 'Ford', 'Transit Connect', 2024, 'Agate Black', 'NV-008', 'Elizabeth Evans', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_019', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00039', 'Ford', 'F-250', 2023, 'Blue Jeans', 'NV-009', 'Charles Edwards', ',territory_west_2,region_west,admin_all,'),
('v_a_w2_020', 'customer_a', 'WEST', 'WEST_2', '1FTFW1E50MFA00040', 'Ford', 'E-Transit', 2024, 'Oxford White', 'NV-010', 'Margaret Collins', ',territory_west_2,region_west,admin_all,');

-- Customer A - EAST Region (35 vehicles)
INSERT INTO vehicles (vehicle_id, customer_id, region_id, territory_id, vin, make, model, year, color, license_plate, driver_name, access_roles) VALUES
('v_a_e1_001', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00041', 'Ford', 'F-150', 2023, 'Oxford White', 'NY-001', 'William Stewart', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_002', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00042', 'Ford', 'Transit', 2023, 'Agate Black', 'NY-002', 'Barbara Sanchez', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_003', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00043', 'Ford', 'E-Transit', 2024, 'Oxford White', 'NY-003', 'Richard Morris', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_004', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00044', 'Ford', 'F-250', 2022, 'Race Red', 'NY-004', 'Linda Rogers', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_005', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00045', 'Ford', 'F-350', 2023, 'Iconic Silver', 'NY-005', 'Thomas Reed', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_006', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00046', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'NJ-001', 'Dorothy Cook', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_007', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00047', 'Ford', 'Transit Connect', 2023, 'Oxford White', 'NJ-002', 'Paul Morgan', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_008', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00048', 'Ford', 'Ranger', 2024, 'Cactus Grey', 'NJ-003', 'Nancy Bell', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_009', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00049', 'Ford', 'F-150', 2023, 'Carbonized Grey', 'NJ-004', 'Edward Murphy', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_010', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00050', 'Ford', 'Transit', 2022, 'Blue Jeans', 'NJ-005', 'Helen Bailey', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_011', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00051', 'Ford', 'E-Transit', 2024, 'Agate Black', 'MA-001', 'Frank Rivera', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_012', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00052', 'Ford', 'F-250', 2024, 'Oxford White', 'MA-002', 'Carol Cooper', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_013', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00053', 'Ford', 'F-150', 2023, 'Atlas Blue', 'MA-003', 'Ronald Richardson', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_014', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00054', 'Ford', 'Transit', 2023, 'Oxford White', 'MA-004', 'Donna Cox', ',territory_east_1,region_east,admin_all,'),
('v_a_e1_015', 'customer_a', 'EAST', 'EAST_1', '1FTFW1E50MFA00055', 'Ford', 'F-350', 2022, 'Agate Black', 'MA-005', 'Kenneth Howard', ',territory_east_1,region_east,admin_all,'),
('v_a_e2_001', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00056', 'Ford', 'F-150', 2024, 'Oxford White', 'FL-001', 'Sharon Ward', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_002', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00057', 'Ford', 'Transit', 2023, 'Race Red', 'FL-002', 'Gary Torres', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_003', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00058', 'Ford', 'E-Transit', 2024, 'Iconic Silver', 'FL-003', 'Ruth Peterson', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_004', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00059', 'Ford', 'F-250', 2023, 'Oxford White', 'FL-004', 'Gregory Gray', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_005', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00060', 'Ford', 'F-150 Lightning', 2024, 'Iced Blue Silver', 'FL-005', 'Deborah Ramirez', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_006', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00061', 'Ford', 'Ranger', 2023, 'Cyber Orange', 'GA-001', 'Steven James', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_007', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00062', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'GA-002', 'Cynthia Watson', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_008', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00063', 'Ford', 'F-350', 2023, 'Agate Black', 'GA-003', 'Larry Brooks', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_009', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00064', 'Ford', 'F-150', 2022, 'Carbonized Grey', 'GA-004', 'Kimberly Kelly', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_010', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00065', 'Ford', 'Transit', 2024, 'Blue Jeans', 'GA-005', 'Dennis Sanders', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_011', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00066', 'Ford', 'E-Transit', 2024, 'Oxford White', 'NC-001', 'Angela Price', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_012', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00067', 'Ford', 'F-250', 2023, 'Race Red', 'NC-002', 'Jerry Bennett', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_013', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00068', 'Ford', 'F-150', 2024, 'Iconic Silver', 'NC-003', 'Marie Wood', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_014', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00069', 'Ford', 'Transit', 2022, 'Oxford White', 'NC-004', 'Ralph Barnes', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_015', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00070', 'Ford', 'Ranger', 2024, 'Agate Black', 'NC-005', 'Joyce Ross', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_016', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00071', 'Ford', 'F-150 Lightning', 2024, 'Oxford White', 'SC-001', 'Roy Henderson', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_017', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00072', 'Ford', 'Transit Connect', 2023, 'Blue Jeans', 'SC-002', 'Diane Coleman', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_018', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00073', 'Ford', 'F-350', 2024, 'Carbonized Grey', 'SC-003', 'Eugene Jenkins', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_019', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00074', 'Ford', 'F-250', 2022, 'Oxford White', 'SC-004', 'Janice Perry', ',territory_east_2,region_east,admin_all,'),
('v_a_e2_020', 'customer_a', 'EAST', 'EAST_2', '1FTFW1E50MFA00075', 'Ford', 'E-Transit', 2024, 'Agate Black', 'SC-005', 'Russell Powell', ',territory_east_2,region_east,admin_all,');

-- Customer A - CENTRAL Region (25 vehicles)
INSERT INTO vehicles (vehicle_id, customer_id, region_id, territory_id, vin, make, model, year, color, license_plate, driver_name, access_roles) VALUES
('v_a_c1_001', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00076', 'Ford', 'F-150', 2023, 'Oxford White', 'IL-001', 'Teresa Long', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_002', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00077', 'Ford', 'Transit', 2024, 'Agate Black', 'IL-002', 'Wayne Patterson', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_003', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00078', 'Ford', 'E-Transit', 2024, 'Iconic Silver', 'IL-003', 'Judy Hughes', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_004', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00079', 'Ford', 'F-250', 2023, 'Race Red', 'IL-004', 'Randy Flores', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_005', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00080', 'Ford', 'F-350', 2022, 'Oxford White', 'MI-001', 'Alice Washington', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_006', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00081', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'MI-002', 'Philip Butler', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_007', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00082', 'Ford', 'Ranger', 2023, 'Cactus Grey', 'MI-003', 'Virginia Simmons', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_008', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00083', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'MI-004', 'Bobby Foster', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_009', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00084', 'Ford', 'F-150', 2022, 'Blue Jeans', 'OH-001', 'Anne Gonzales', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_010', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00085', 'Ford', 'Transit', 2023, 'Carbonized Grey', 'OH-002', 'Lawrence Bryant', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_011', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00086', 'Ford', 'E-Transit', 2024, 'Oxford White', 'OH-003', 'Julia Alexander', ',territory_central_1,region_central,admin_all,'),
('v_a_c1_012', 'customer_a', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFA00087', 'Ford', 'F-250', 2024, 'Agate Black', 'OH-004', 'Jesse Russell', ',territory_central_1,region_central,admin_all,'),
('v_a_c2_001', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00088', 'Ford', 'F-150', 2023, 'Oxford White', 'MO-001', 'Kathryn Griffin', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_002', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00089', 'Ford', 'Transit', 2022, 'Race Red', 'MO-002', 'Jack Diaz', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_003', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00090', 'Ford', 'F-350', 2024, 'Iconic Silver', 'MO-003', 'Beverly Hayes', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_004', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00091', 'Ford', 'E-Transit', 2024, 'Oxford White', 'KS-001', 'Albert Myers', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_005', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00092', 'Ford', 'F-250', 2023, 'Carbonized Grey', 'KS-002', 'Gloria Ford', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_006', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00093', 'Ford', 'F-150 Lightning', 2024, 'Atlas Blue', 'KS-003', 'Randy Hamilton', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_007', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00094', 'Ford', 'Ranger', 2023, 'Oxford White', 'MN-001', 'Debra Graham', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_008', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00095', 'Ford', 'Transit Connect', 2024, 'Agate Black', 'MN-002', 'Jeremy Sullivan', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_009', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00096', 'Ford', 'F-150', 2022, 'Blue Jeans', 'MN-003', 'Marilyn Wallace', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_010', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00097', 'Ford', 'Transit', 2024, 'Oxford White', 'MN-004', 'Carl West', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_011', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00098', 'Ford', 'E-Transit', 2024, 'Iconic Silver', 'WI-001', 'Cheryl Cole', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_012', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00099', 'Ford', 'F-350', 2023, 'Race Red', 'WI-002', 'Terry Jordan', ',territory_central_2,region_central,admin_all,'),
('v_a_c2_013', 'customer_a', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFA00100', 'Ford', 'F-250', 2024, 'Oxford White', 'WI-003', 'Nicole Owens', ',territory_central_2,region_central,admin_all,');

-- Customer B - BlueStar Transport (100 vehicles - similar distribution)
INSERT INTO vehicles (vehicle_id, customer_id, region_id, territory_id, vin, make, model, year, color, license_plate, driver_name, access_roles) VALUES
('v_b_w1_001', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00001', 'Ford', 'F-150', 2023, 'Oxford White', 'WA-B01', 'Adam Stone', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_002', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00002', 'Ford', 'Transit', 2024, 'Agate Black', 'WA-B02', 'Brenda Sharp', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_003', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00003', 'Ford', 'E-Transit', 2024, 'Oxford White', 'WA-B03', 'Craig Dunn', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_004', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00004', 'Ford', 'F-250', 2023, 'Race Red', 'WA-B04', 'Dana Cross', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_005', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00005', 'Ford', 'F-350', 2022, 'Iconic Silver', 'WA-B05', 'Earl Chapman', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_006', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00006', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'WA-B06', 'Fiona Burgess', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_007', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00007', 'Ford', 'Ranger', 2023, 'Cactus Grey', 'WA-B07', 'Gordon Chambers', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_008', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00008', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'WA-B08', 'Holly Ferguson', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_009', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00009', 'Ford', 'F-150', 2022, 'Blue Jeans', 'OR-B01', 'Ivan Garrett', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_010', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00010', 'Ford', 'Transit', 2023, 'Carbonized Grey', 'OR-B02', 'Jackie Harper', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_011', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00011', 'Ford', 'E-Transit', 2024, 'Agate Black', 'OR-B03', 'Keith Hoffman', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_012', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00012', 'Ford', 'F-250', 2024, 'Oxford White', 'OR-B04', 'Lori Ingram', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_013', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00013', 'Ford', 'F-150', 2023, 'Race Red', 'OR-B05', 'Mike Jacobs', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_014', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00014', 'Ford', 'Transit', 2022, 'Oxford White', 'ID-B01', 'Nora Keller', ',territory_west_1,region_west,admin_all,'),
('v_b_w1_015', 'customer_b', 'WEST', 'WEST_1', '1FTFW1E50MFB00015', 'Ford', 'F-350', 2024, 'Iconic Silver', 'ID-B02', 'Oscar Lambert', ',territory_west_1,region_west,admin_all,'),
('v_b_w2_001', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00016', 'Ford', 'F-150', 2023, 'Oxford White', 'AZ-B01', 'Paula Manning', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_002', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00017', 'Ford', 'Transit', 2024, 'Blue Jeans', 'AZ-B02', 'Quinn Newman', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_003', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00018', 'Ford', 'E-Transit', 2024, 'Agate Black', 'AZ-B03', 'Rita Olson', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_004', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00019', 'Ford', 'F-250', 2022, 'Carbonized Grey', 'AZ-B04', 'Sam Payne', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_005', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00020', 'Ford', 'F-150 Lightning', 2024, 'Oxford White', 'AZ-B05', 'Tina Quinn', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_006', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00021', 'Ford', 'Ranger', 2023, 'Cyber Orange', 'NM-B01', 'Victor Reeves', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_007', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00022', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'NM-B02', 'Wendy Shaw', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_008', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00023', 'Ford', 'F-350', 2023, 'Race Red', 'NM-B03', 'Xavier Torres', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_009', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00024', 'Ford', 'F-150', 2024, 'Iconic Silver', 'NM-B04', 'Yvonne Underwood', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_010', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00025', 'Ford', 'Transit', 2022, 'Agate Black', 'NM-B05', 'Zack Vaughn', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_011', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00026', 'Ford', 'E-Transit', 2024, 'Oxford White', 'CO-B01', 'Amber Warren', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_012', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00027', 'Ford', 'F-250', 2023, 'Blue Jeans', 'CO-B02', 'Brandon Xavier', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_013', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00028', 'Ford', 'F-150', 2022, 'Oxford White', 'CO-B03', 'Carmen Young', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_014', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00029', 'Ford', 'Transit', 2024, 'Carbonized Grey', 'CO-B04', 'Derek Zimmerman', ',territory_west_2,region_west,admin_all,'),
('v_b_w2_015', 'customer_b', 'WEST', 'WEST_2', '1FTFW1E50MFB00030', 'Ford', 'Ranger', 2024, 'Cactus Grey', 'CO-B05', 'Elena Adams', ',territory_west_2,region_west,admin_all,'),
('v_b_e1_001', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00031', 'Ford', 'F-150', 2023, 'Oxford White', 'NY-B01', 'Felix Brown', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_002', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00032', 'Ford', 'Transit', 2024, 'Agate Black', 'NY-B02', 'Gina Clark', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_003', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00033', 'Ford', 'E-Transit', 2024, 'Iconic Silver', 'NY-B03', 'Henry Davis', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_004', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00034', 'Ford', 'F-250', 2023, 'Race Red', 'NY-B04', 'Irene Evans', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_005', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00035', 'Ford', 'F-350', 2022, 'Oxford White', 'PA-B01', 'John Foster', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_006', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00036', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'PA-B02', 'Karen Green', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_007', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00037', 'Ford', 'Ranger', 2023, 'Blue Jeans', 'PA-B03', 'Leo Harris', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_008', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00038', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'PA-B04', 'Maria Irving', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_009', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00039', 'Ford', 'F-150', 2022, 'Carbonized Grey', 'PA-B05', 'Nathan Johnson', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_010', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00040', 'Ford', 'Transit', 2023, 'Agate Black', 'CT-B01', 'Olivia King', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_011', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00041', 'Ford', 'E-Transit', 2024, 'Oxford White', 'CT-B02', 'Peter Lee', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_012', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00042', 'Ford', 'F-250', 2024, 'Race Red', 'CT-B03', 'Quinn Miller', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_013', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00043', 'Ford', 'F-150', 2023, 'Iconic Silver', 'CT-B04', 'Rachel Nelson', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_014', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00044', 'Ford', 'Transit', 2022, 'Blue Jeans', 'CT-B05', 'Steve Owen', ',territory_east_1,region_east,admin_all,'),
('v_b_e1_015', 'customer_b', 'EAST', 'EAST_1', '1FTFW1E50MFB00045', 'Ford', 'F-350', 2024, 'Oxford White', 'ME-B01', 'Tracy Parker', ',territory_east_1,region_east,admin_all,'),
('v_b_e2_001', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00046', 'Ford', 'F-150', 2023, 'Agate Black', 'FL-B01', 'Uma Quinn', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_002', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00047', 'Ford', 'Transit', 2024, 'Oxford White', 'FL-B02', 'Victor Ross', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_003', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00048', 'Ford', 'E-Transit', 2024, 'Carbonized Grey', 'FL-B03', 'Wendy Smith', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_004', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00049', 'Ford', 'F-250', 2022, 'Race Red', 'FL-B04', 'Xavier Taylor', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_005', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00050', 'Ford', 'F-150 Lightning', 2024, 'Iced Blue Silver', 'FL-B05', 'Yolanda Upton', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_006', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00051', 'Ford', 'Ranger', 2023, 'Iconic Silver', 'GA-B01', 'Zachary Vance', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_007', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00052', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'GA-B02', 'Abby Wagner', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_008', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00053', 'Ford', 'F-350', 2023, 'Agate Black', 'GA-B03', 'Ben Xander', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_009', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00054', 'Ford', 'F-150', 2024, 'Blue Jeans', 'GA-B04', 'Clara Yates', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_010', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00055', 'Ford', 'Transit', 2022, 'Oxford White', 'GA-B05', 'Derek Zane', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_011', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00056', 'Ford', 'E-Transit', 2024, 'Race Red', 'VA-B01', 'Emma Abbott', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_012', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00057', 'Ford', 'F-250', 2023, 'Iconic Silver', 'VA-B02', 'Frank Barnes', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_013', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00058', 'Ford', 'F-150', 2022, 'Carbonized Grey', 'VA-B03', 'Grace Carter', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_014', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00059', 'Ford', 'Transit', 2024, 'Agate Black', 'VA-B04', 'Harold Dixon', ',territory_east_2,region_east,admin_all,'),
('v_b_e2_015', 'customer_b', 'EAST', 'EAST_2', '1FTFW1E50MFB00060', 'Ford', 'Ranger', 2024, 'Oxford White', 'VA-B05', 'Iris Edwards', ',territory_east_2,region_east,admin_all,'),
('v_b_c1_001', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00061', 'Ford', 'F-150', 2023, 'Blue Jeans', 'IL-B01', 'James Ford', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_002', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00062', 'Ford', 'Transit', 2024, 'Oxford White', 'IL-B02', 'Kelly Grant', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_003', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00063', 'Ford', 'E-Transit', 2024, 'Agate Black', 'IL-B03', 'Larry Hill', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_004', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00064', 'Ford', 'F-250', 2023, 'Race Red', 'IL-B04', 'Monica Ivy', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_005', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00065', 'Ford', 'F-350', 2022, 'Iconic Silver', 'IN-B01', 'Nick James', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_006', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00066', 'Ford', 'F-150 Lightning', 2024, 'Antimatter Blue', 'IN-B02', 'Olivia Kent', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_007', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00067', 'Ford', 'Ranger', 2023, 'Cactus Grey', 'IN-B03', 'Paul Lane', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_008', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00068', 'Ford', 'Transit Connect', 2024, 'Oxford White', 'IN-B04', 'Quinn Moore', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_009', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00069', 'Ford', 'F-150', 2022, 'Carbonized Grey', 'IN-B05', 'Rachel Nash', ',territory_central_1,region_central,admin_all,'),
('v_b_c1_010', 'customer_b', 'CENTRAL', 'CENTRAL_1', '1FTFW1E50MFB00070', 'Ford', 'Transit', 2023, 'Agate Black', 'WI-B01', 'Sam Owen', ',territory_central_1,region_central,admin_all,'),
('v_b_c2_001', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00071', 'Ford', 'F-150', 2024, 'Oxford White', 'MO-B01', 'Tina Price', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_002', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00072', 'Ford', 'Transit', 2022, 'Blue Jeans', 'MO-B02', 'Ulrich Quinn', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_003', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00073', 'Ford', 'E-Transit', 2024, 'Race Red', 'MO-B03', 'Victoria Reed', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_004', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00074', 'Ford', 'F-250', 2023, 'Iconic Silver', 'MO-B04', 'William Scott', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_005', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00075', 'Ford', 'F-350', 2024, 'Oxford White', 'IA-B01', 'Xena Taylor', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_006', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00076', 'Ford', 'F-150 Lightning', 2024, 'Atlas Blue', 'IA-B02', 'Yuri Upton', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_007', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00077', 'Ford', 'Ranger', 2023, 'Agate Black', 'IA-B03', 'Zara Vance', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_008', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00078', 'Ford', 'Transit Connect', 2024, 'Carbonized Grey', 'IA-B04', 'Aaron Wells', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_009', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00079', 'Ford', 'F-150', 2022, 'Oxford White', 'IA-B05', 'Betty Xavier', ',territory_central_2,region_central,admin_all,'),
('v_b_c2_010', 'customer_b', 'CENTRAL', 'CENTRAL_2', '1FTFW1E50MFB00080', 'Ford', 'Transit', 2024, 'Blue Jeans', 'NE-B01', 'Carl Young', ',territory_central_2,region_central,admin_all,');

-- =============================================================================
-- INITIAL VEHICLE STATE
-- =============================================================================

-- Insert initial vehicle_state for all vehicles (will be updated by Kafka consumer)
INSERT INTO vehicle_state (vehicle_id, last_seen_ts, status, lat, lon, speed, heading, fuel_pct, engine_temp, battery_v, odometer)
SELECT 
    vehicle_id,
    NOW(6),
    'active',
    CASE 
        WHEN region_id = 'WEST' AND territory_id = 'WEST_1' THEN 47.6062 + (RAND() * 2 - 1)
        WHEN region_id = 'WEST' AND territory_id = 'WEST_2' THEN 33.4484 + (RAND() * 2 - 1)
        WHEN region_id = 'EAST' AND territory_id = 'EAST_1' THEN 40.7128 + (RAND() * 2 - 1)
        WHEN region_id = 'EAST' AND territory_id = 'EAST_2' THEN 28.5383 + (RAND() * 2 - 1)
        WHEN region_id = 'CENTRAL' AND territory_id = 'CENTRAL_1' THEN 41.8781 + (RAND() * 2 - 1)
        ELSE 39.0997 + (RAND() * 2 - 1)
    END,
    CASE 
        WHEN region_id = 'WEST' AND territory_id = 'WEST_1' THEN -122.3321 + (RAND() * 2 - 1)
        WHEN region_id = 'WEST' AND territory_id = 'WEST_2' THEN -112.0740 + (RAND() * 2 - 1)
        WHEN region_id = 'EAST' AND territory_id = 'EAST_1' THEN -74.0060 + (RAND() * 2 - 1)
        WHEN region_id = 'EAST' AND territory_id = 'EAST_2' THEN -81.3792 + (RAND() * 2 - 1)
        WHEN region_id = 'CENTRAL' AND territory_id = 'CENTRAL_1' THEN -87.6298 + (RAND() * 2 - 1)
        ELSE -94.5786 + (RAND() * 2 - 1)
    END,
    ROUND(RAND() * 65, 2),
    ROUND(RAND() * 360, 2),
    ROUND(50 + RAND() * 50, 2),
    ROUND(180 + RAND() * 30, 2),
    ROUND(12.0 + RAND() * 2, 2),
    FLOOR(10000 + RAND() * 90000)
FROM vehicles;

-- =============================================================================
-- DRIVER NOTES (for AI summarization demo)
-- =============================================================================

INSERT INTO driver_notes (note_id, vehicle_id, customer_id, driver_id, driver_name, ts, note_text, category, region_id, territory_id, access_roles) VALUES
('note_001', 'v_a_w1_001', 'customer_a', 'driver_001', 'John Smith', DATE_SUB(NOW(), INTERVAL 2 DAY), 'Noticed slight vibration at highway speeds around 70mph. May need tire balance check at next service.', 'maintenance', 'WEST', 'WEST_1', ',territory_west_1,region_west,admin_all,'),
('note_002', 'v_a_w1_002', 'customer_a', 'driver_002', 'Sarah Johnson', DATE_SUB(NOW(), INTERVAL 1 DAY), 'Delivered all packages on route early today. New traffic pattern on I-5 is much better than the old route.', 'operations', 'WEST', 'WEST_1', ',territory_west_1,region_west,admin_all,'),
('note_003', 'v_a_w1_003', 'customer_a', 'driver_003', 'Mike Davis', DATE_SUB(NOW(), INTERVAL 3 DAY), 'Check engine light came on briefly but went away. Fuel economy seems lower than usual this week.', 'maintenance', 'WEST', 'WEST_1', ',territory_west_1,region_west,admin_all,'),
('note_004', 'v_a_e1_001', 'customer_a', 'driver_041', 'William Stewart', DATE_SUB(NOW(), INTERVAL 1 DAY), 'Heavy traffic delays on route through Manhattan. Suggest adjusting delivery windows for downtown customers.', 'operations', 'EAST', 'EAST_1', ',territory_east_1,region_east,admin_all,'),
('note_005', 'v_a_e1_002', 'customer_a', 'driver_042', 'Barbara Sanchez', DATE_SUB(NOW(), INTERVAL 4 HOUR), 'Brake pads making squeaking noise. Scheduled for service next week but may need to move it up.', 'maintenance', 'EAST', 'EAST_1', ',territory_east_1,region_east,admin_all,'),
('note_006', 'v_a_c1_001', 'customer_a', 'driver_076', 'Teresa Long', DATE_SUB(NOW(), INTERVAL 6 HOUR), 'Great day on the road. All deliveries completed ahead of schedule. Customer at 5th stop gave excellent feedback.', 'operations', 'CENTRAL', 'CENTRAL_1', ',territory_central_1,region_central,admin_all,'),
('note_007', 'v_b_w1_001', 'customer_b', 'driver_b001', 'Adam Stone', DATE_SUB(NOW(), INTERVAL 12 HOUR), 'AC not cooling properly in the afternoon heat. May need refrigerant recharge before summer gets worse.', 'maintenance', 'WEST', 'WEST_1', ',territory_west_1,region_west,admin_all,'),
('note_008', 'v_b_e1_001', 'customer_b', 'driver_b031', 'Felix Brown', DATE_SUB(NOW(), INTERVAL 2 DAY), 'Found efficient shortcut through Brooklyn that saves 15 minutes on morning route. Will document for team.', 'operations', 'EAST', 'EAST_1', ',territory_east_1,region_east,admin_all,'),
('note_009', 'v_a_w1_004', 'customer_a', 'driver_004', 'Emily Chen', DATE_SUB(NOW(), INTERVAL 5 HOUR), 'E-Transit performed excellently today. Completed full route with 35% battery remaining. Charging now.', 'operations', 'WEST', 'WEST_1', ',territory_west_1,region_west,admin_all,'),
('note_010', 'v_a_w2_001', 'customer_a', 'driver_021', 'Carlos Hernandez', DATE_SUB(NOW(), INTERVAL 8 HOUR), 'Transmission shifting roughly between 2nd and 3rd gear. Scheduling diagnostic check this week.', 'maintenance', 'WEST', 'WEST_2', ',territory_west_2,region_west,admin_all,');

