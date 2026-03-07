"""
Database Migration Script for Projects
Run this to create projects table and update datasets table
"""
import mysql.connector
from config import Config

def run_projects_migration():
    connection = None
    cursor = None
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        
        print("✅ Connected to database")
        
        # Create projects table
        print("\n📋 Creating projects table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                status ENUM('active', 'completed', 'archived') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Projects table created successfully")
        
        # Check if project_id column already exists in datasets
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'datasets' 
            AND COLUMN_NAME = 'project_id'
        """, (Config.MYSQL_DB,))
        
        column_exists = cursor.fetchone()[0] > 0
        
        if not column_exists:
            print("\n📋 Adding project_id column to datasets table...")
            cursor.execute("""
                ALTER TABLE datasets 
                ADD COLUMN project_id INT
            """)
            print("✅ project_id column added")
            
            # Add foreign key constraint
            print("\n📋 Adding foreign key constraint...")
            try:
                cursor.execute("""
                    ALTER TABLE datasets
                    ADD CONSTRAINT fk_datasets_project 
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                """)
                print("✅ Foreign key constraint added")
            except mysql.connector.Error as err:
                if "Duplicate" in str(err):
                    print("ℹ️  Foreign key constraint already exists")
                else:
                    raise
            
            # Create index on project_id
            cursor.execute("""
                CREATE INDEX idx_datasets_project_id ON datasets(project_id)
            """)
            print("✅ Index created on project_id")
        else:
            print("ℹ️  project_id column already exists in datasets table")
        
        connection.commit()
        print("\n🎉 Projects migration completed successfully!")
        
    except Exception as err:
        print(f"❌ Error: {err}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n✅ Database connection closed")

if __name__ == '__main__':
    print("=" * 50)
    print("PROJECTS TABLE MIGRATION")
    print("=" * 50)
    run_projects_migration()
