from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from datetime import timedelta

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

def mydb():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost/postgres"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secretkey'

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    
    return app
