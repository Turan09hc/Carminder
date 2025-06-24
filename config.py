# carminder/config.py
import os

# Database connection settings - UPDATE THESE FOR YOUR SETUP:
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'  # Change to your MySQL username
MYSQL_PASSWORD = 'Turan2006' 
MYSQL_DB = 'carminder'
MYSQL_CURSORCLASS = 'DictCursor'

# Flask configuration
SECRET_KEY = 'carminder-secret-key-2025-change-this-in-production'

# Session configuration
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

# Application settings
DEBUG = True

# Alternative configuration using environment variables (recommended for production)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'carminder-secret-key-2025-change-this-in-production'
    
    # MySQL Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'carminder'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    