"""
Rebuild users table with correct structure
WARNING: This will delete all existing users!
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def rebuild_users_table():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        
        print("\n" + "=" * 60)
        print("⚠️  REBUILDING USERS TABLE")
        print("=" * 60)
        
        # Drop existing users table
        print("\n🗑️  Dropping old users table...")
        cursor.execute("DROP TABLE IF EXISTS users")
        print("✅ Old table dropped")
        
        # Create new users table with correct structure
        print("\n📋 Creating new users table...")
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ New users table created with password_hash column")
        
        # Create test user 'loki'
        print("\n👤 Creating user 'loki'...")
        password_hash = generate_password_hash('loki123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            ('loki', 'loki@example.com', password_hash)
        )
        
        connection.commit()
        print("✅ User 'loki' created!")
        
        # Verify
        cursor.execute("SELECT id, username, email FROM users WHERE username = 'loki'")
        user = cursor.fetchone()
        
        if user:
            print(f"\n✅ Verified: User ID {user[0]} - {user[1]} ({user[2]})")
        
        print("\n" + "=" * 60)
        print("🎉 TABLE REBUILT SUCCESSFULLY!")
        print("=" * 60)
        print("\n  ✅ Users table has correct structure")
        print("  ✅ Test user created")
        print("\n" + "=" * 60)
        print("YOU CAN NOW LOGIN:")
        print("=" * 60)
        print("\n  Username: loki")
        print("  Password: loki123")
        print("\n  URL: http://127.0.0.1:5000/auth/login")
        print("\n" + "=" * 60)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    rebuild_users_table()
