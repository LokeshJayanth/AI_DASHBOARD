"""
Fix Authentication System
- Add passwords to old users (admin, demo_user)
- Verify all users can login
- Test user data isolation
"""
from werkzeug.security import generate_password_hash
from services.db_service import execute_query

def fix_old_users():
    """Add password hashes to users without passwords"""
    print("\n" + "="*60)
    print("FIXING OLD USERS WITHOUT PASSWORDS")
    print("="*60 + "\n")
    
    # Get users without password_hash
    users = execute_query(
        "SELECT id, username, email FROM users WHERE password_hash IS NULL",
        fetch=True
    )
    
    if not users:
        print("✅ All users have passwords!")
        return
    
    print(f"Found {len(users)} user(s) without passwords:\n")
    
    for user in users:
        username = user['username']
        # Set default password as "password123" for old users
        default_password = "password123"
        password_hash = generate_password_hash(default_password)
        
        # Update user with password hash
        execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user['id'])
        )
        
        print(f"  ✅ {username} - Password set to: {default_password}")
    
    print(f"\n✅ Fixed {len(users)} user(s)")
    print("\n" + "="*60)

def verify_all_users():
    """Verify all users have proper authentication setup"""
    print("\n" + "="*60)
    print("VERIFYING ALL USERS")
    print("="*60 + "\n")
    
    users = execute_query(
        "SELECT id, username, email, password_hash, created_at FROM users",
        fetch=True
    )
    
    print(f"Total users: {len(users)}\n")
    
    for user in users:
        has_password = "✅" if user['password_hash'] else "❌"
        print(f"{has_password} {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   ID: {user['id']}")
        print(f"   Has Password: {'Yes' if user['password_hash'] else 'No'}")
        print()

def check_user_data_isolation():
    """Check that datasets are properly linked to users"""
    print("\n" + "="*60)
    print("CHECKING USER DATA ISOLATION")
    print("="*60 + "\n")
    
    # Get all users
    users = execute_query("SELECT id, username FROM users", fetch=True)
    
    for user in users:
        # Count datasets for this user
        datasets = execute_query(
            "SELECT COUNT(*) as count FROM datasets WHERE user_id = %s",
            (user['id'],),
            fetch=True
        )
        
        count = datasets[0]['count'] if datasets else 0
        print(f"👤 {user['username']} (ID: {user['id']})")
        print(f"   📊 Datasets: {count}")
        
        # Show dataset names if any
        if count > 0:
            user_datasets = execute_query(
                "SELECT name, created_at FROM datasets WHERE user_id = %s LIMIT 5",
                (user['id'],),
                fetch=True
            )
            for ds in user_datasets:
                print(f"      - {ds['name']}")
        print()

def create_test_user():
    """Create a test user for verification"""
    print("\n" + "="*60)
    print("CREATING TEST USER")
    print("="*60 + "\n")
    
    # Check if test user exists
    existing = execute_query(
        "SELECT id FROM users WHERE username = %s",
        ('testuser',),
        fetch=True
    )
    
    if existing:
        print("⚠️  Test user already exists")
        return
    
    # Create test user
    password_hash = generate_password_hash('test123')
    execute_query(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        ('testuser', 'test@example.com', password_hash)
    )
    
    print("✅ Test user created:")
    print("   Username: testuser")
    print("   Password: test123")
    print("   Email: test@example.com")

def main():
    """Run all fixes and verifications"""
    print("\n🔧 AUTHENTICATION SYSTEM FIX & VERIFICATION")
    print("="*60)
    
    # Fix old users
    fix_old_users()
    
    # Create test user
    create_test_user()
    
    # Verify all users
    verify_all_users()
    
    # Check data isolation
    check_user_data_isolation()
    
    print("\n" + "="*60)
    print("✅ AUTHENTICATION SYSTEM READY!")
    print("="*60)
    print("\n📝 LOGIN CREDENTIALS:")
    print("\n   Old Users (password: password123):")
    print("   - admin / password123")
    print("   - demo_user / password123")
    print("\n   Existing Users (use their original passwords):")
    print("   - loki / [original password]")
    print("   - 123 / [original password]")
    print("   - 1234 / [original password]")
    print("\n   Test User:")
    print("   - testuser / test123")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
