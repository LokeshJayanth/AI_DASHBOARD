"""
Check users table structure
"""
import mysql.connector
from config import Config

def check_table_structure():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        
        print("\n" + "=" * 60)
        print("USERS TABLE STRUCTURE")
        print("=" * 60)
        
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        print("\nColumns:")
        for col in columns:
            print(f"  • {col[0]} ({col[1]})")
        
        print("\n" + "=" * 60)
        print("ALL USERS IN DATABASE")
        print("=" * 60)
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if users:
            print(f"\nFound {len(users)} users:")
            for user in users:
                print(f"  {user}")
        else:
            print("\nNo users found!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_table_structure()
