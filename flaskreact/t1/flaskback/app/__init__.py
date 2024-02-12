from flask import Flask,make_response
import os
from flask_sqlalchemy import SQLALchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS



db=SQLALchemy()

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    db.__init__(app)
    Migrate(app,db)

    with app.app_context():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin","*")
    
    CORS(app,resources=r'/api/*')

    

    return app