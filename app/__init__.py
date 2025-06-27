import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    mysql.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    return app