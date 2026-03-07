from services.db_service import get_db_connection

try:
    conn = get_db_connection()
    if conn:
        print("✅ MySQL Connected Successfully")
        print(f"✅ Database: ai_dashboard")
        print(f"✅ Host: localhost:3306")
        conn.close()
    else:
        print("❌ Connection failed")
except Exception as e:
    print(f"❌ Error: {e}")
