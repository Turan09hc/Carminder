# carminder/config.py
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-this-in-production'
    
    # MySQL Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'your_mysql_password'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'carminder'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    
# For development - you can use this simple configuration
# Make sure to change these values for production!

# Database connection settings - UPDATE THESE:
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'  # Change to your MySQL username
MYSQL_PASSWORD = ''  # Change to your MySQL password
MYSQL_DB = 'carminder'
SECRET_KEY = 'carminder-secret-key-2025'