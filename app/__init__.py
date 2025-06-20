from flask import Flask
from flask import current_app
from flask_mysqldb import MySQL  

mysql = MySQL()  

def create_app():
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_pyfile('../config.py')

    # Initialize DB
    mysql.init_app(app)

    # Import and register routes
    from .routes import main
    app.register_blueprint(main)

    return app
