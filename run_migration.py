"""
Run database migrations to create dashboards table
"""
import mysql.connector
import os
from config import Config

# Read the migration SQL file
migration_file = 'migrations/create_dashboards_table.sql'

with open(migration_file, 'r') as f:
    sql_content = f.read()

# Connect to database
try:
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )
    
    cursor = conn.cursor()
    
    # Split SQL statements and execute them
    statements = sql_content.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                print(f"✅ Executed: {statement[:50]}...")
            except mysql.connector.Error as err:
                if 'Duplicate column name' in str(err) or 'already exists' in str(err):
                    print(f"⚠️  Skipped (already exists): {statement[:50]}...")
                else:
                    print(f"❌ Error: {err}")
                    print(f"   Statement: {statement[:100]}...")
    
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
    # Verify table was created
    cursor.execute("SHOW TABLES LIKE 'dashboards'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Dashboards table exists!")
        
        # Show table structure
        cursor.execute("DESCRIBE dashboards")
        columns = cursor.fetchall()
        print("\n📊 Dashboards table structure:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
    else:
        print("❌ Dashboards table was not created!")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Database error: {err}")
except Exception as e:
    print(f"❌ Error: {e}")
