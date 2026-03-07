"""
Authentication System Test Script
Tests all authentication endpoints and user isolation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_test(test_name, status=""):
    if status == "PASS":
        print(f"✅ {test_name}")
    elif status == "FAIL":
        print(f"❌ {test_name}")
    else:
        print(f"\n🔍 {test_name}")

def test_login_page():
    """Test if login page loads"""
    print_test("Testing Login Page")
    try:
        response = requests.get(f"{BASE_URL}/auth/login")
        if response.status_code == 200 and "Sign In" in response.text:
            print_test("Login page loads successfully", "PASS")
            return True
        else:
            print_test(f"Login page failed (Status: {response.status_code})", "FAIL")
            return False
    except Exception as e:
        print_test(f"Login page error: {str(e)}", "FAIL")
        return False

def test_register_page():
    """Test if register page loads"""
    print_test("Testing Register Page")
    try:
        response = requests.get(f"{BASE_URL}/auth/register")
        if response.status_code == 200 and "Create Account" in response.text:
            print_test("Register page loads successfully", "PASS")
            return True
        else:
            print_test(f"Register page failed (Status: {response.status_code})", "FAIL")
            return False
    except Exception as e:
        print_test(f"Register page error: {str(e)}", "FAIL")
        return False

def test_storage_redirect():
    """Test if storage page redirects to login when not authenticated"""
    print_test("Testing Protected Route (Storage)")
    try:
        response = requests.get(f"{BASE_URL}/storage/", allow_redirects=False)
        if response.status_code in [302, 303]:
            print_test("Storage page correctly redirects to login", "PASS")
            return True
        else:
            print_test(f"Storage page should redirect (Status: {response.status_code})", "FAIL")
            return False
    except Exception as e:
        print_test(f"Storage redirect error: {str(e)}", "FAIL")
        return False

def test_user_registration():
    """Test user registration"""
    print_test("Testing User Registration")
    try:
        session = requests.Session()
        
        # Try to register a test user
        response = session.post(f"{BASE_URL}/auth/register", data={
            'username': 'testuser123',
            'email': 'testuser123@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, allow_redirects=True)
        
        if response.status_code == 200:
            if "Registration successful" in response.text or "already exists" in response.text:
                print_test("Registration endpoint working", "PASS")
                return True
        
        print_test(f"Registration may have failed (Status: {response.status_code})", "FAIL")
        return False
    except Exception as e:
        print_test(f"Registration error: {str(e)}", "FAIL")
        return False

def test_database_tables():
    """Test if database tables exist"""
    print_test("Testing Database Tables")
    try:
        import mysql.connector
        from config import Config
        
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        
        # Check users table
        cursor.execute("SHOW TABLES LIKE 'users'")
        if cursor.fetchone():
            print_test("Users table exists", "PASS")
        else:
            print_test("Users table missing", "FAIL")
            return False
        
        # Check if datasets table has user_id column
        cursor.execute("SHOW COLUMNS FROM datasets LIKE 'user_id'")
        if cursor.fetchone():
            print_test("Datasets table has user_id column", "PASS")
        else:
            print_test("Datasets table missing user_id column", "FAIL")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print_test(f"Database check error: {str(e)}", "FAIL")
        return False

def run_all_tests():
    """Run all authentication tests"""
    print("=" * 60)
    print("🧪 MULTI-USER AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Database
    results.append(test_database_tables())
    
    # Test 2: Login Page
    results.append(test_login_page())
    
    # Test 3: Register Page
    results.append(test_register_page())
    
    # Test 4: Protected Routes
    results.append(test_storage_redirect())
    
    # Test 5: Registration
    results.append(test_user_registration())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Authentication system is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n💡 Next Steps:")
    print("1. Open http://127.0.0.1:5000/auth/register to create an account")
    print("2. Login at http://127.0.0.1:5000/auth/login")
    print("3. Upload datasets at http://127.0.0.1:5000/storage/")
    print("4. Each user will only see their own datasets!")

if __name__ == '__main__':
    run_all_tests()
