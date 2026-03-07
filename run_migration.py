"""
Database Migration Script
Run this to create the users table and update datasets table
"""
import mysql.connector
from config import Config

def run_migration():
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
        
        # Create users table
        print("\n📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Users table created successfully")
        
        # Check if user_id column already exists in datasets
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'datasets' 
            AND COLUMN_NAME = 'user_id'
        """, (Config.MYSQL_DB,))
        
        column_exists = cursor.fetchone()[0] > 0
        
        if not column_exists:
            print("\n📋 Adding user_id column to datasets table...")
            # Add user_id column to datasets table
            cursor.execute("""
                ALTER TABLE datasets 
                ADD COLUMN user_id INT
            """)
            print("✅ user_id column added")
            
            # Add foreign key constraint
            print("\n📋 Adding foreign key constraint...")
            cursor.execute("""
                ALTER TABLE datasets
                ADD CONSTRAINT fk_datasets_user 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Foreign key constraint added")
            
            # Create index on user_id
            cursor.execute("""
                CREATE INDEX idx_datasets_user_id ON datasets(user_id)
            """)
            print("✅ Index created on user_id")
        else:
            print("ℹ️  user_id column already exists in datasets table")
        
        connection.commit()
        print("\n🎉 Migration completed successfully!")
        
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
    print("DATABASE MIGRATION")
    print("=" * 50)
    run_migration()
