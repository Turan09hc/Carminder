CREATE DATABASE IF NOT EXISTS carminder;
USE carminder;
CREATE TABLE cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    palate_number VARCHAR(20) UNIQUE NOT NULL,
    car_model VARCHAR(100) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    tel_no VARCHAR(20) NOT NULL,
    milage INT NOT NULL,
    production_date DATE NOT NULL,
    gas_type VARCHAR(20) NOT NULL,
    oil_type VARCHAR(20) NOT NULL,
    last_oil_change_km INT DEFAULT 0,
    last_oil_change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Optional: Create maintenance history table
CREATE TABLE maintenance_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT,
    maintenance_type ENUM('oil_change', 'filter_change', 'inspection', 'other') NOT NULL,
    mileage_at_service INT NOT NULL,
    service_date DATE NOT NULL,
    notes TEXT,
    cost DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
);