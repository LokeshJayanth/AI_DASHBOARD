-- AI Dashboard Database Schema

CREATE DATABASE IF NOT EXISTS ai_dashboard;
USE ai_dashboard;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    table_name VARCHAR(255),
    user_id INT,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_table_name (table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Prompts/Queries table
CREATE TABLE IF NOT EXISTS prompts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    dataset_id INT,
    prompt_text TEXT NOT NULL,
    response_text LONGTEXT,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    processing_time DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Metadata for uploaded files
CREATE TABLE IF NOT EXISTS file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    metadata_key VARCHAR(255) NOT NULL,
    metadata_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_metadata_key (metadata_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data
INSERT INTO users (username, email) VALUES 
('admin', 'admin@example.com'),
('demo_user', 'demo@example.com');
