"""
Check Users in Database
Quick script to see if any users exist
"""
import mysql.connector
from config import Config

def check_users():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)
        
        # Get all users
        cursor.execute("SELECT id, username, email, created_at FROM users")
        users = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print("USERS IN DATABASE")
        print("=" * 60)
        
        if users:
            print(f"\n✅ Found {len(users)} user(s):\n")
            for user in users:
                print(f"  • ID: {user['id']}")
                print(f"    Username: {user['username']}")
                print(f"    Email: {user['email']}")
                print(f"    Created: {user['created_at']}")
                print()
        else:
            print("\n❌ No users found in database!")
            print("\n💡 You need to register first!")
            print("   Go to: http://127.0.0.1:5000/auth/register")
            print()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_users()
