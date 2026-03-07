"""
Quick User Setup - Create a test user or reset password
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def setup_test_user():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)
        
        print("\n" + "=" * 60)
        print("USER SETUP")
        print("=" * 60)
        
        # Check if lokesh user exists
        cursor.execute("SELECT * FROM users WHERE username = 'lokesh'")
        existing = cursor.fetchone()
        
        if existing:
            print("\n⚠️  User 'lokesh' already exists!")
            print("   Updating password to 'lokesh123'...")
            
            password_hash = generate_password_hash('lokesh123')
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'lokesh'",
                (password_hash,)
            )
            connection.commit()
            print("✅ Password updated successfully!")
        else:
            print("\n📝 Creating new user 'lokesh'...")
            
            password_hash = generate_password_hash('lokesh123')
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ('lokesh', 'lokesh@example.com', password_hash)
            )
            connection.commit()
            print("✅ User created successfully!")
        
        print("\n" + "=" * 60)
        print("🎉 YOU CAN NOW LOGIN WITH:")
        print("=" * 60)
        print("\n  Username: lokesh")
        print("  Password: lokesh123")
        print("\n  URL: http://127.0.0.1:5000/auth/login")
        print("\n" + "=" * 60)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    setup_test_user()
