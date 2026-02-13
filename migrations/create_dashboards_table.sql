-- Create dashboards table to store AUTO MODE dashboard states
-- This allows users to save and re-open their analytics dashboards

USE ai_dashboard;

CREATE TABLE IF NOT EXISTS dashboards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dataset_id INT NOT NULL,
    user_id INT NOT NULL,
    project_id INT,
    mode ENUM('auto', 'prompt') DEFAULT 'auto',
    
    -- Dashboard State (JSON)
    stats_data JSON,           -- All KPI cards data
    charts_data JSON,          -- All charts configuration and data
    insights_data JSON,        -- AI-generated insights
    
    -- Files
    preview_image VARCHAR(500), -- Path to dashboard preview screenshot
    powerbi_file VARCHAR(500),  -- Path to .pbix file
    csv_file VARCHAR(500),      -- Path to cleaned CSV
    
    -- Metadata
    total_charts INT DEFAULT 0,
    total_kpis INT DEFAULT 0,
    dataset_rows INT,
    dataset_columns INT,
    
    -- Status
    status ENUM('draft', 'published', 'archived') DEFAULT 'published',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_viewed_at TIMESTAMP NULL,
    
    -- Foreign Keys
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_project_id (project_id),
    INDEX idx_mode (mode),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add columns to datasets table to track if dashboard exists
ALTER TABLE datasets 
ADD COLUMN IF NOT EXISTS has_dashboard BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS dashboard_id INT NULL,
ADD COLUMN IF NOT EXISTS rows INT NULL,
ADD COLUMN IF NOT EXISTS columns INT NULL;
