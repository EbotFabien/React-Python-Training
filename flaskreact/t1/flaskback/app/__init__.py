from flask import Flask,make_response
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS



db=SQLAlchemy()

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    db.__init__(app)
    Migrate(app,db)

    with app.app_context():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin","*")
    
    CORS(app,resources=r'/api/*')

    from app.api import api as api_blueprint
    from app.api.v1.fake import fake as fake_blueprint
    from app import models

    app.register_blueprint(api_blueprint,url_prefix='/api')
    app.register_blueprint(fake_blueprint)

    

    return app