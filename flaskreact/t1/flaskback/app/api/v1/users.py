import json
from flask_restx import Namespace,Resource,fields,marshal,Api 
import jwt,os 
from flask_cors import CORS

from functools import wraps
from flask import request,Blueprint
from flask import current_app as app

from app.models import Post,User,Token
from werkzeug.datastructures import FileStorage
from app import db

authorizations ={
    'KEY':{
        'type':'apiKey',
        'in':'header',
        'name':'Authorization'
    }
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token =None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
            try:
                data=User.verify_access_token(token)
                
                if not data:
                    return {'message':'Token is invalid.'},401
            except:
                return {'message':'Token is invalid.'},401
            

        if not token:
            return {'message':'Token is missing or nor found'}
        
        if data:
            pass
        return f(*args, **kwargs)
    
    return decorated


api = Blueprint('api',__name__)
user_doc=Api(app=api,doc='/docs',version='1.4',title='Blog',authorizations=authorizations)

CORS(api,resources={r"/api/*":{"origins":"*"}})

uploader = user_doc.parser()
uploader.add_argument('file',location='files',type=FileStorage,required=False,help="You must parse a file")

uploader.add_argument('name',location='form',type=str,required=False,help="Name cannot be blank")


user_space=user_doc.namespace('/api/user',\
                              description="All routes under this section of the documentation are the open routes bot can perform\
                        CRUD action on the application",\
                            path='/v1/')

user_data = user_space.model('user_data',{
    "id":fields.Integer(required=False,default="",description="Identity"),
    "username":fields.String(required=False,default="",description="Username"),
    "email":fields.String(required=False,default="",description="Email"),
    "avatar_url":fields.String(required=False,default="",description="avatar"),
    "about_me":fields.String(required=False,default="",description="about me"),
    "last_seen":fields.String(required=False,default="",description="last seen"),
    "first_seen":fields.String(required=False,default="",description="last seen"),
})

user_create_data = user_space.model('user_create_data',{
    "username":fields.String(required=False,default="",description="username"),
    "email":fields.String(required=False,default="",description="email"),
    "password":fields.String(required=False,default="",description="password"),
})

@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/users')
class all(Resource):
    @token_required
    def get(self):
        if request.args:
            page = int(request.args.get('page', None))
            per_page = int(request.args.get('per_page', None))

        
        #token=request.headers['Authorization']
        #data =jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        users_=User.query.paginate(page=page,per_page=per_page)

        return{
            "results":marshal(users_.items,user_data)
        }


@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/me')
class single(Resource):
    @token_required
    def get(self):
        
        token=request.headers['Authorization'].split()[1]
        
        user=User.verify_access_token(token)
        

        return{
            "results":marshal(user,user_data)
        }


@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/me')
class edit_me(Resource):
    @token_required
    def put(self):
        
        data=request.get_json()
        token=request.headers['Authorization'].split()[1]
        
        user=User.verify_access_token(token)
        if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
            return {},400

        user.update(data)
        db.session.commit()
        

        return{
            "results":marshal(user,user_data)
        }



@user_space.doc(
    security='KEY',
    params={
            
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/user/create/')
class create(Resource):
    @user_space.expect(user_create_data)
    def post(self):
        data=request.get_json()
        user= User(username=data["username"], email=data["email"],
                    about_me='',password_hash=data["password"])
        db.session.add(user)
        db.session.commit()
        return{
            "results":marshal(user,user_data),
            "res":"User created succesfully"
        },200


@user_space.doc(
    security='KEY',
    params={
            
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/users/<username>')
class get_by_username(Resource):
    @token_required
    def get(self,username):
        if request.args:
            page = int(request.args.get('page', None))
            per_page = int(request.args.get('per_page', None))

        
        
        users_=User.query.filter_by(username=username).first()

        return{
            "results":marshal(users_,user_data)
        },200


@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/me/following/<int:id>')
class is_followed(Resource):
    @token_required
    def get(self,id):
        
        token=request.headers['Authorization'].split()[1]
        
        user=User.verify_access_token(token)
        followed_user = User.query.filter_by(id=id).first() 

        if not user.is_following(followed_user):
            return {},404
        return {},204
        

        

@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/me/following/<int:id>')
class follow_user(Resource):
    @token_required
    def post(self,id):
        
        token=request.headers['Authorization'].split()[1]
        
        user=User.verify_access_token(token)
        followed_user = User.query.filter_by(id=id).first() 

        if user.is_following(followed_user):
            return {},404
        user.follow(followed_user)
        db.session.commit()
        return {},204


@user_space.doc(
    security='KEY',
    params={
            'page': 'Value to start from ',
            'per_page':'Number of pages'
    },
    responses={
         200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@user_space.route('/me/following/<int:id>')
class unfollow_user(Resource):
    @token_required
    def delete(self,id):
        
        token=request.headers['Authorization'].split()[1]
        
        user=User.verify_access_token(token)
        unfollowed_user = User.query.filter_by(id=id).first() 

        if not user.is_following(unfollowed_user):
            return {},404
        user.unfollow(unfollowed_user)
        db.session.commit()
        return {},204
        

        

        