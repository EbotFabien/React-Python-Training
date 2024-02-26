from datetime import datetime, timedelta
import json
import time
from flask import current_app,url_for
import jwt
from app import db
import secrets

from werkzeug.security import generate_password_hash,check_password_hash

import uuid


followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('users.id'))
)

class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)

class Token(db.Model):
    __tablename__ = 'tokens'

    id= db.Column(db.Integer,primary_key=True)
    access_token=db.Column(db.String(64),index=True)
    refresh_token = db.Column(db.String(64),index=True)
    refresh_expiration = db.Column(db.DateTime())
    access_expiration = db.Column(db.DateTime())
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    #user_tokens=db.relationship(
    #    'User',backref='tokens'
    #)

    @property
    def access_token_jwt(self):
        return jwt.encode({'token':self.access_token},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256')
    
    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token =secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])
        
    def expire(self,delay=None):
        if delay is None:
            delay = 5 if not current_app.testing else 0
        self.access_expiration = datetime.utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = datetime.utcnow() + timedelta(seconds=delay)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        Token.query.where(
            Token.refresh_expiration < yesterday).delete()
        db.session.commit()

    @staticmethod
    def from_jwt(access_token_jwt):
        access_token = None
        try:
            access_token = jwt.decode(access_token_jwt,
                                      current_app.config['SECRET_KEY'],
                                      algorithms=['HS256'])['token']
            return Token.query.filter_by(access_token=access_token).first()
        except jwt.PyJWTError:
            pass

class User(Updateable,db.Model):
    __tablename__='users'

    id=db.Column(db.Integer,primary_key=True)
    uuid = db.Column(db.String,unique=True)
    username =db.Column(db.String,unique=True)
    email = db.Column(db.String,nullable=False)
    password_hash = db.Column(db.String,nullable=True)
    about_me = db.Column(db.String)
    first_seen = db.Column(db.DateTime(),default=datetime.utcnow,nullable=False)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow,nullable=False)

    tokens=db.relationship(
        'Token',
        backref='user'
    )
    posts=db.relationship(
        'Post',
        backref='author', lazy='dynamic'
    )

    following = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic'
    )

    

    def followed_posts_select(self):
        followed=Post.query.join(
            followers,(followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        
        own = Post.query.filter_by(user_id=self.id)
        
        return followed.union(own).order_by(Post.timestamp.desc())


    def __init__(self,username,email,about_me,password_hash):
        self.username =username
        self.email=email
        self.uuid=str(uuid.uuid4())
        self.password_hash=generate_password_hash(password_hash)
        self.about_me=about_me

    def __repr__(self):
        return '<User %r>' % self.username
    
    @property
    def url(self):
        return  url_for('users.get',id=self.id)
    
    @property
    def has_password(self):
        return self.password_hash is not None
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        if self.password_hash:
            return check_password_hash(self.password_hash,password)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
    
    def follow(self,user):
        if not self.is_following(user):
            self.following.append(user)
    
    def unfollow(self,user):
        if self.is_following(user):
            self.following.remove(user)
    
    def is_following(self,user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def generate_auth_token(self):
        token=Token(user=self)
        token.generate()
        return token 
    
    @staticmethod
    def verify_access_token(acess_token_jwt,refresh_token=None):
        token = Token.from_jwt(acess_token_jwt)
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user
    
    @staticmethod
    def verify_refresh_token(refresh_token,access_token_jwt):
        token=Token.from_jwt(access_token_jwt)
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > datetime.utcnow():
                return token
            
            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        Token.delete().where(Token.user == self)
        db.session.commit()

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp':time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email':self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return User.filter_by(email=data['reset_email']).first()

class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    text=db.Column(db.String)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)
    #author = db.relationship('User',backref='posts',lazy='dynamic')


    #def __init__(self,text,user):
    #    self.user_id=user
    #    self.text=text
        
    
    def __repr__(self):
        return '<Post %r>' % self.id
    
    @property
    def url(self):
        return url_for('posts.get',id=self.id)




