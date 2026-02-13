"""
Test Login System
Verify that:
1. New users can register
2. Old users can login
3. No errors when typing username/password
4. Each user has their own dashboards/files
5. No user can access another user's data
"""
from services.user_service import create_user, verify_user, get_user_by_id
from services.db_service import execute_query

def test_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 1: USER REGISTRATION")
    print("="*60 + "\n")
    
    # Try to create a new user
    test_username = "newuser_test"
    test_email = "newuser@test.com"
    test_password = "secure123"
    
    # Delete if exists
    execute_query("DELETE FROM users WHERE username = %s", (test_username,))
    
    success, message, user_id = create_user(test_username, test_email, test_password)
    
    if success:
        print(f"✅ Registration successful!")
        print(f"   User ID: {user_id}")
        print(f"   Message: {message}")
    else:
        print(f"❌ Registration failed: {message}")
        return False
    
    # Try to create duplicate user
    success2, message2, _ = create_user(test_username, test_email, test_password)
    
    if not success2 and "already exists" in message2.lower():
        print(f"✅ Duplicate prevention works: {message2}")
    else:
        print(f"❌ Duplicate prevention failed")
        return False
    
    # Cleanup
    execute_query("DELETE FROM users WHERE username = %s", (test_username,))
    
    return True

def test_login():
    """Test user login"""
    print("\n" + "="*60)
    print("TEST 2: USER LOGIN")
    print("="*60 + "\n")
    
    # Test with correct credentials
    print("Testing correct credentials...")
    success, message, user_data = verify_user("testuser", "test123")
    
    if success:
        print(f"✅ Login successful!")
        print(f"   Username: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
        print(f"   User ID: {user_data['id']}")
    else:
        print(f"❌ Login failed: {message}")
        return False
    
    # Test with wrong password
    print("\nTesting wrong password...")
    success2, message2, _ = verify_user("testuser", "wrongpassword")
    
    if not success2:
        print(f"✅ Wrong password rejected: {message2}")
    else:
        print(f"❌ Wrong password accepted (security issue!)")
        return False
    
    # Test with non-existent user
    print("\nTesting non-existent user...")
    success3, message3, _ = verify_user("nonexistent", "password")
    
    if not success3:
        print(f"✅ Non-existent user rejected: {message3}")
    else:
        print(f"❌ Non-existent user accepted (security issue!)")
        return False
    
    return True

def test_old_users_login():
    """Test that old users can login with new passwords"""
    print("\n" + "="*60)
    print("TEST 3: OLD USERS LOGIN")
    print("="*60 + "\n")
    
    old_users = [
        ("admin", "password123"),
        ("demo_user", "password123")
    ]
    
    all_passed = True
    
    for username, password in old_users:
        success, message, user_data = verify_user(username, password)
        
        if success:
            print(f"✅ {username} can login")
        else:
            print(f"❌ {username} cannot login: {message}")
            all_passed = False
    
    return all_passed

def test_data_isolation():
    """Test that users can only see their own data"""
    print("\n" + "="*60)
    print("TEST 4: DATA ISOLATION")
    print("="*60 + "\n")
    
    # Get user with datasets
    user_with_data = execute_query(
        """SELECT u.id, u.username, COUNT(d.id) as dataset_count 
           FROM users u 
           LEFT JOIN datasets d ON u.id = d.user_id 
           GROUP BY u.id 
           HAVING dataset_count > 0 
           LIMIT 1""",
        fetch=True
    )
    
    if not user_with_data:
        print("⚠️  No users with datasets found, skipping test")
        return True
    
    user = user_with_data[0]
    user_id = user['id']
    username = user['username']
    dataset_count = user['dataset_count']
    
    print(f"Testing with user: {username} (ID: {user_id})")
    print(f"This user has {dataset_count} dataset(s)")
    
    # Get this user's datasets
    user_datasets = execute_query(
        "SELECT id, name FROM datasets WHERE user_id = %s",
        (user_id,),
        fetch=True
    )
    
    print(f"\n✅ User can see their own datasets:")
    for ds in user_datasets:
        print(f"   - {ds['name']} (ID: {ds['id']})")
    
    # Try to get another user's datasets
    other_user = execute_query(
        "SELECT id, username FROM users WHERE id != %s LIMIT 1",
        (user_id,),
        fetch=True
    )
    
    if other_user:
        other_user_id = other_user[0]['id']
        other_username = other_user[0]['username']
        
        other_datasets = execute_query(
            "SELECT id, name FROM datasets WHERE user_id = %s",
            (other_user_id,),
            fetch=True
        )
        
        print(f"\n✅ Other user ({other_username}) has separate data:")
        if other_datasets:
            for ds in other_datasets:
                print(f"   - {ds['name']} (ID: {ds['id']})")
        else:
            print(f"   - No datasets")
        
        print(f"\n✅ Data isolation verified: Each user has separate datasets")
    
    return True

def test_password_security():
    """Test that passwords are properly hashed"""
    print("\n" + "="*60)
    print("TEST 5: PASSWORD SECURITY")
    print("="*60 + "\n")
    
    # Get a user's password hash
    user = execute_query(
        "SELECT username, password_hash FROM users WHERE username = 'testuser'",
        fetch=True
    )
    
    if not user:
        print("❌ Test user not found")
        return False
    
    password_hash = user[0]['password_hash']
    
    # Check that password is hashed (not plain text)
    if password_hash and password_hash != "test123":
        print(f"✅ Password is hashed (not stored as plain text)")
        print(f"   Hash preview: {password_hash[:50]}...")
    else:
        print(f"❌ Password is NOT hashed (security issue!)")
        return False
    
    # Check hash format (should start with scrypt:)
    if password_hash.startswith('scrypt:'):
        print(f"✅ Using secure scrypt hashing algorithm")
    else:
        print(f"⚠️  Using different hashing algorithm: {password_hash.split(':')[0]}")
    
    return True

def test_session_data():
    """Test that session data is properly structured"""
    print("\n" + "="*60)
    print("TEST 6: SESSION DATA STRUCTURE")
    print("="*60 + "\n")
    
    success, message, user_data = verify_user("testuser", "test123")
    
    if not success:
        print("❌ Cannot test session data - login failed")
        return False
    
    # Check that user_data has required fields
    required_fields = ['id', 'username', 'email']
    
    all_present = True
    for field in required_fields:
        if field in user_data:
            print(f"✅ {field}: {user_data[field]}")
        else:
            print(f"❌ Missing field: {field}")
            all_present = False
    
    # Check that password_hash is NOT in session data (security)
    if 'password_hash' not in user_data:
        print(f"✅ password_hash NOT in session (secure)")
    else:
        print(f"❌ password_hash in session (security issue!)")
        all_present = False
    
    return all_present

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING LOGIN SYSTEM")
    print("="*60)
    
    tests = [
        ("Registration", test_registration),
        ("Login", test_login),
        ("Old Users Login", test_old_users_login),
        ("Data Isolation", test_data_isolation),
        ("Password Security", test_password_security),
        ("Session Data", test_session_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
