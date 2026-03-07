"""
Fix users table by adding password_hash column (safer approach - no data loss)
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def fix_users_table():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)
        
        print("\n" + "=" * 60)
        print("FIXING USERS TABLE")
        print("=" * 60)
        
        # Check if password_hash column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
        has_password_hash = cursor.fetchone()
        
        if not has_password_hash:
            print("\n📋 Adding password_hash column...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
            print("✅ password_hash column added")
            
            # If there's a password column, copy data
            cursor.execute("SHOW COLUMNS FROM users LIKE 'password'")
            has_password = cursor.fetchone()
            
            if has_password:
                print("\n📋 Copying data from password to password_hash...")
                cursor.execute("UPDATE users SET password_hash = password WHERE password_hash IS NULL")
                print("✅ Data copied")
        else:
            print("\n✅ password_hash column already exists")
        
        connection.commit()
        
        # Now create the test user
        print("\n👤 Creating/Updating user 'loki'...")
        
        # Delete if exists
        cursor.execute("DELETE FROM users WHERE username = 'loki'")
        
        # Create new
        password_hash = generate_password_hash('loki123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            ('loki', 'loki@example.com', password_hash)
        )
        connection.commit()
        print("✅ User 'loki' created successfully!")
        
        # Verify
        cursor.execute("SELECT id, username, email FROM users WHERE username = 'loki'")
        user = cursor.fetchone()
        
        if user:
            print(f"\n✅ Verified: User ID {user['id']} - {user['username']} ({user['email']})")
        
        print("\n" + "=" * 60)
        print("🎉 USERS TABLE FIXED!")
        print("=" * 60)
        print("\nYOU CAN NOW LOGIN:")
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
    fix_users_table()
