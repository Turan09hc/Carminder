-- Enhanced CarMinder Database Schema - Building on your existing structure
CREATE DATABASE IF NOT EXISTS carminder CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE carminder;

-- Drop existing tables in correct order (your current structure)
DROP TABLE IF EXISTS maintenance_history;
DROP TABLE IF EXISTS cars;

-- Drop new tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS car_models;

-- Companies table for multi-tenant support
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    language VARCHAR(50) NOT NULL,
    business_size VARCHAR(50) NOT NULL,
    primary_interest VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Users table for authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'manager', 'employee') DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Car models lookup table
CREATE TABLE car_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year_from INT DEFAULT 2000,
    year_to INT DEFAULT 2025,
    fuel_type ENUM('gasoline', 'diesel', 'hybrid', 'electric') DEFAULT 'gasoline',
    engine_size VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced cars table with company isolation (building on your structure)
CREATE TABLE cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    plate_number VARCHAR(20) NOT NULL,
    car_model_id INT NULL,
    custom_model VARCHAR(100),
    owner VARCHAR(100) NOT NULL,
    tel_no VARCHAR(20) NOT NULL,
    mileage INT NOT NULL,
    production_date DATE NOT NULL,
    gas_type VARCHAR(20) NOT NULL,
    oil_type VARCHAR(50) NOT NULL,
    last_oil_change_km INT DEFAULT 0,
    last_oil_change_date DATE DEFAULT (CURRENT_DATE),
    created_by INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (car_model_id) REFERENCES car_models(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE KEY unique_plate_per_company (company_id, plate_number)
);

-- Enhanced maintenance history (same as your structure + company isolation)
CREATE TABLE maintenance_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT NOT NULL,
    company_id INT NOT NULL,
    maintenance_type ENUM('oil_change', 'filter_change', 'brake_service', 'inspection', 'other') NOT NULL,
    mileage_at_service INT NOT NULL,
    service_date DATE NOT NULL,
    notes TEXT,
    cost DECIMAL(10,2) DEFAULT 0.00,
    performed_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id)
);

-- Insert popular car models
INSERT INTO car_models (brand, model, year_from, year_to, fuel_type, engine_size) VALUES
-- Toyota
('Toyota', 'Camry', 2010, 2025, 'gasoline', '2.0L'),
('Toyota', 'Camry', 2010, 2025, 'gasoline', '2.5L'),
('Toyota', 'Corolla', 2010, 2025, 'gasoline', '1.6L'),
('Toyota', 'Corolla', 2010, 2025, 'gasoline', '1.8L'),
('Toyota', 'RAV4', 2015, 2025, 'gasoline', '2.0L'),
('Toyota', 'Prius', 2010, 2025, 'hybrid', '1.8L'),
('Toyota', 'Land Cruiser', 2010, 2025, 'gasoline', '4.0L'),
('Toyota', 'Land Cruiser', 2010, 2025, 'diesel', '4.5L'),

-- Honda
('Honda', 'Civic', 2010, 2025, 'gasoline', '1.5L'),
('Honda', 'Civic', 2010, 2025, 'gasoline', '2.0L'),
('Honda', 'Accord', 2010, 2025, 'gasoline', '2.0L'),
('Honda', 'CR-V', 2015, 2025, 'gasoline', '1.5L'),

-- Nissan
('Nissan', 'Altima', 2010, 2025, 'gasoline', '2.5L'),
('Nissan', 'Sentra', 2010, 2025, 'gasoline', '1.8L'),
('Nissan', 'Rogue', 2015, 2025, 'gasoline', '2.5L'),
('Nissan', 'Xtrail', 2005, 2025, 'gasoline', '2.5L'),

-- Hyundai
('Hyundai', 'Elantra', 2010, 2025, 'gasoline', '2.0L'),
('Hyundai', 'Sonata', 2010, 2025, 'gasoline', '2.4L'),
('Hyundai', 'Tucson', 2015, 2025, 'gasoline', '2.0L'),

-- BMW
('BMW', '3 Series', 2010, 2025, 'gasoline', '2.0L'),
('BMW', '3 Series', 2010, 2025, 'diesel', '2.0L'),
('BMW', '5 Series', 2010, 2025, 'gasoline', '3.0L'),
('BMW', 'X3', 2015, 2025, 'gasoline', '2.0L'),

-- Mercedes-Benz
('Mercedes-Benz', 'C-Class', 2010, 2025, 'gasoline', '2.0L'),
('Mercedes-Benz', 'E-Class', 2010, 2025, 'gasoline', '3.0L'),
('Mercedes-Benz', 'E-Class', 2010, 2025, 'diesel', '2.2L'),

-- Audi
('Audi', 'A4', 2010, 2025, 'gasoline', '2.0L'),
('Audi', 'A4', 2010, 2025, 'diesel', '2.0L'),
('Audi', 'A6', 2010, 2025, 'gasoline', '3.0L'),

-- Popular in Azerbaijan/Turkey region
('Lada', 'Granta', 2015, 2025, 'gasoline', '1.6L'),
('Lada', 'Vesta', 2015, 2025, 'gasoline', '1.6L'),
('Renault', 'Logan', 2010, 2025, 'gasoline', '1.6L'),
('Renault', 'Sandero', 2010, 2025, 'gasoline', '1.6L'),
('Dacia', 'Duster', 2015, 2025, 'gasoline', '1.6L'),

-- Ford
('Ford', 'Focus', 2010, 2025, 'gasoline', '2.0L'),
('Ford', 'Fusion', 2010, 2025, 'gasoline', '2.5L'),

-- Volkswagen
('Volkswagen', 'Jetta', 2010, 2025, 'gasoline', '1.4L'),
('Volkswagen', 'Passat', 2010, 2025, 'gasoline', '1.8L'),
('Volkswagen', 'Passat', 2010, 2025, 'diesel', '2.0L');

--Mitsubishi
('Mitsubishi', 'ASX', 2010, 2025, 'gasoline', '2.0L'),
('Mitsubishi', 'Lancer', 2000, 2010, 'gasoline', '2.0L'),

--Byd
('Byd', 'Tang', 2020, 2025, 'electric', '0.0L'),
('Byd', 'Song+', 2020, 2025, 'electric', '0.0L'),

-- Create demo company and user for testing
INSERT INTO companies (company_name, owner_name, email, phone, country, language, business_size, primary_interest) 
VALUES ('Demo Auto Service', 'Demo Owner', 'demo@carminder.com', '+994501234567', 'Azerbaijan', 'English', '1-5 vehicles', 'Fleet Management');

-- Create demo admin user (password: admin123)
INSERT INTO users (company_id, username, email, password_hash, full_name, role) 
VALUES (1, 'admin', 'demo@carminder.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXIG/QHuCdve', 'Demo Owner', 'admin');