import json
from flask_restx import Namespace,Resource,fields,marshal,Api 
import jwt,os 
from flask_cors import CORS

from functools import wraps
from flask import Blueprint, request, abort, current_app as app, url_for, session
from werkzeug.http import dump_cookie

from app.models import Post,User,Token
from werkzeug.datastructures import FileStorage
from app import db
import base64

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
            token = request.headers['Authorization']
            try:
                data=jwt.decode(token,app.config.get('SECRET_KEY'))
            except:
                return {'message':'Token is invalid.'},401
            

        if not token:
            return {'message':'Token is missing or nor found'},403
        
        if data:
            pass
        return f(*args, **kwargs)
    
    return decorated


api = Blueprint('api',__name__)
token_doc=Api(app=api,doc='/docs',version='1.4',title='Blog',authorizations=authorizations)

CORS(api,resources={r"/api/*":{"origins":"*"}})

uploader = token_doc.parser()
uploader.add_argument('file',location='files',type=FileStorage,required=False,help="You must parse a file")

uploader.add_argument('name',location='form',type=str,required=False,help="Name cannot be blank")


token_space=token_doc.namespace('/api/token',\
                              description="All routes under this section of the documentation are the open routes bot can perform\
                        CRUD action on the application",\
                            path='/v1/')

user_data = token_space.model('user_data',{
    "id":fields.Integer(required=False,default="",description="Identity"),
    "username":fields.String(required=False,default="",description="Username"),
    "email":fields.String(required=False,default="",description="Email"),
    "avatar_url":fields.String(required=False,default="",description="avatar"),
    "about_me":fields.String(required=False,default="",description="about me"),
    "last_seen":fields.String(required=False,default="",description="last seen"),
    "first_seen":fields.String(required=False,default="",description="last seen"),
})

user_create_data = token_space.model('user_create_data',{
    "username":fields.String(required=False,default="",description="username"),
    "email":fields.String(required=False,default="",description="email"),
    "password":fields.String(required=False,default="",description="password"),
})

def token_response(token):
    headers = {}
    if app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if app.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not app.debug else 'lax'
        headers['Set-Cookie'] = dump_cookie(
            'refresh_token', token.refresh_token,
            path=url_for('api./api/token_new'), secure=not app.debug,
            httponly=True, samesite=samesite)
    return {
        'access_token': token.access_token_jwt,
        'refresh_token': token.refresh_token
        if app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200, headers


@token_space.doc(
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

@token_space.route('/tokens')
class new(Resource):
    def post(self):
        data_=base64.b64decode(request.headers['Authorization'].split()[1])
        data=data_.decode('utf-8').split(':')
        username=data[0]
        password=data[1]
        check=User.query.filter_by(username=username).first()
        if check is None:
            check=User.query.filter_by(email=username).first()
        if check and check.verify_password(password):
            token = check.generate_auth_token()
            db.session.add(token)
            Token.clean()
            db.session.commit()
            return token_response(token)

                
@token_space.doc(
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

@token_space.route('/tokens')
class refresh(Resource):
    def put(self):
        
        access_token_jwt = args['access_token']
        refresh_token = args.get('refresh_token',request.cookies.get('refresh_token'))
        if not access_token_jwt or not refresh_token:
            abort(401)
        token = User.verify_refresh_token(refresh_token, access_token_jwt)
        if not token:
            abort(401)
        token.expire()
        new_token = token.user.generate_auth_token()
        db.session.add_all([token, new_token])
        db.session.commit()
        return token_response(new_token)
        