import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
from flask_mysqldb import MySQL
from datetime import timedelta

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Session configuration for authentication
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    mysql.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    return app