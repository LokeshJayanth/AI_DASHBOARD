"""
User Service
Handles user-related database operations
"""
from services.db_service import execute_query
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, email, password):
    """
    Create a new user with hashed password
    Returns (success, message, user_id)
    """
    try:
        # Check if username already exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s",
            (username,),
            fetch=True
        )
        if existing_user:
            return False, "Username already exists", None
        
        # Check if email already exists
        existing_email = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        if existing_email:
            return False, "Email already registered", None
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        execute_query(query, (username, email, password_hash))
        
        # Get the new user's ID
        user = execute_query(
            "SELECT id FROM users WHERE username = %s",
            (username,),
            fetch=True
        )
        user_id = user[0]['id'] if user else None
        
        return True, "User created successfully", user_id
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False, f"Error creating user: {str(e)}", None

def verify_user(username, password):
    """
    Verify user credentials
    Returns (success, message, user_data)
    """
    try:
        # Get user from database
        user = execute_query(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s",
            (username,),
            fetch=True
        )
        
        if not user:
            return False, "Invalid username or password", None
        
        user_data = user[0]
        
        # Check password
        if check_password_hash(user_data['password_hash'], password):
            return True, "Login successful", {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email']
            }
        else:
            return False, "Invalid username or password", None
            
    except Exception as e:
        print(f"Error verifying user: {str(e)}")
        return False, f"Error: {str(e)}", None

def get_user_by_id(user_id):
    """
    Get user information by ID
    Returns user data dictionary or None
    """
    try:
        user = execute_query(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,),
            fetch=True
        )
        return user[0] if user else None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def get_user_by_username(username):
    """
    Get user information by username
    Returns user data dictionary or None
    """
    try:
        user = execute_query(
            "SELECT id, username, email, created_at FROM users WHERE username = %s",
            (username,),
            fetch=True
        )
        return user[0] if user else None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
