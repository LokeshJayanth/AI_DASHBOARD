import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize database connection on app startup"""
    connection = get_db_connection()
    if connection:
        print("✅ Database connection successful!")
        connection.close()
    else:
        print("❌ Database connection failed!")

def execute_query(query, params=None, fetch=False):
    """Execute a query with optional parameters"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
        
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Database error: {e}")
        return None

def get_all_datasets(user_id=None):
    """Get all datasets, optionally filtered by user"""
    query = "SELECT * FROM datasets"
    params = None
    
    if user_id:
        query += " WHERE user_id = %s"
        params = (user_id,)
    
    query += " ORDER BY created_at DESC"
    return execute_query(query, params, fetch=True)

def get_dataset_by_id(dataset_id):
    """Get a specific dataset by ID"""
    query = "SELECT * FROM datasets WHERE id = %s"
    result = execute_query(query, (dataset_id,), fetch=True)
    return result[0] if result else None

def create_dataset(name, description, file_path, file_type, file_size, user_id=1, project_id=None):
    """Create a new dataset record"""
    query = """
        INSERT INTO datasets (name, description, file_path, file_type, file_size, user_id, project_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed')
    """
    params = (name, description, file_path, file_type, file_size, user_id, project_id)
    return execute_query(query, params)

def get_all_prompts(user_id=None):
    """Get all prompts, optionally filtered by user"""
    query = """
        SELECT p.*, d.name as dataset_name 
        FROM prompts p 
        LEFT JOIN datasets d ON p.dataset_id = d.id
    """
    params = None
    
    if user_id:
        query += " WHERE p.user_id = %s"
        params = (user_id,)
    
    query += " ORDER BY p.created_at DESC"
    return execute_query(query, params, fetch=True)

def create_prompt(user_id, dataset_id, prompt_text):
    """Create a new prompt/query"""
    query = """
        INSERT INTO prompts (user_id, dataset_id, prompt_text, status)
        VALUES (%s, %s, %s, 'pending')
    """
    params = (user_id, dataset_id, prompt_text)
    return execute_query(query, params)

def update_prompt_response(prompt_id, response_text, status='completed', processing_time=None):
    """Update prompt with response"""
    query = """
        UPDATE prompts 
        SET response_text = %s, status = %s, processing_time = %s
        WHERE id = %s
    """
    params = (response_text, status, processing_time, prompt_id)
    return execute_query(query, params)
