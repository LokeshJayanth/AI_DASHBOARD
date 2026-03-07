"""
Create user 'loki' with correct table structure
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def create_user_properly():
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
        
        # First check table structure
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        print(f"\nTable columns: {column_names}")
        
        # Delete existing loki user if exists
        cursor.execute("DELETE FROM users WHERE username = 'loki'")
        connection.commit()
        
        # Create user with correct column names
        password_hash = generate_password_hash('loki123')
        
        if 'password_hash' in column_names:
            # New table structure
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ('loki', 'loki@example.com', password_hash)
            )
        elif 'password' in column_names:
            # Old table structure
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                ('loki', 'loki@example.com', password_hash)
            )
        else:
            print("❌ Cannot find password column!")
            return
        
        connection.commit()
        
        print("\n✅ User 'loki' created successfully!")
        
        # Verify
        cursor.execute("SELECT id, username, email FROM users WHERE username = 'loki'")
        user = cursor.fetchone()
        
        if user:
            print(f"\n✅ Verified: User ID {user['id']} - {user['username']} ({user['email']})")
        
        print("\n" + "=" * 60)
        print("🎉 YOU CAN NOW LOGIN:")
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
    create_user_properly()
