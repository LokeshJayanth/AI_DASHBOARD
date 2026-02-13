"""
Create user with username: loki
Password: loki123
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def create_loki_user():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)
        
        print("\n" + "=" * 60)
        print("CREATING USER: loki")
        print("=" * 60)
        
        # Check if loki exists
        cursor.execute("SELECT * FROM users WHERE username = 'loki'")
        existing = cursor.fetchone()
        
        if existing:
            print("\n⚠️  User 'loki' already exists! Updating password...")
            password_hash = generate_password_hash('loki123')
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'loki'",
                (password_hash,)
            )
        else:
            print("\n✅ Creating new user 'loki'...")
            password_hash = generate_password_hash('loki123')
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ('loki', 'loki@example.com', password_hash)
            )
        
        connection.commit()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! YOU CAN NOW LOGIN:")
        print("=" * 60)
        print("\n  Username: loki")
        print("  Password: loki123")
        print("\n  URL: http://127.0.0.1:5000/auth/login")
        print("\n" + "=" * 60)
        
        # Verify it works
        print("\n🔍 Verifying login credentials...")
        cursor.execute("SELECT username, email FROM users WHERE username = 'loki'")
        user = cursor.fetchone()
        if user:
            print(f"✅ User found: {user['username']} ({user['email']})")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_loki_user()
