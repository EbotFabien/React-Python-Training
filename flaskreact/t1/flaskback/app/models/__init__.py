from datetime import datetime
import json
from flask import current_app
import jwt
from app import db

from werkzeug.security import generate_password_hash,check_password_hash

import uuid



class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uuid = db.Column(db.String,unique=True)
    username =db.Column(db.String,unique=True)
    email = db.Column(db.String,nullable=False)
    password_hash = db.Column(db.String,nullable=False)

    def __init__(self,username,email,password_hash):
        self.username =username
        self.email=email
        self.uuid=uuid.uuid4.hex()
        self.password_hash=generate_password_hash(password_hash)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    


class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uuid=db.Column(db.String,unique=True)
    content=db.Column(db.String)
    title = db.Column(db.String,unique=True)

    def __init__(self,title,content):
        self.content=content
        self.title=title
        self.uuid=uuid.uuid4.hex()
    
    def __repr__(self):
        return '<Post %r>' % self.title




