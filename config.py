import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Base Directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'  # Store sessions in filesystem for larger data
    
    # Database Config - Update the password below with your actual MySQL password
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '12345'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'ai_dashboard'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    
    # File Upload Config
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads', 'raw_files')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size (increased from 16MB)
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'json'}
    
    # Session Config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
