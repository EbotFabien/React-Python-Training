import json
from flask_restx import Namespace,Resource,fields,marshal,Api 
import jwt,os 
from flask_cors import CORS

from functools import wraps
from flask import request,Blueprint
from flask import current_app as app

from app.models import Post,User,Token
from werkzeug.datastructures import FileStorage


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
                data=Token.from_jwt(token)
                
                if not data:
                    return {'message':'Token is invalid.'},401
            except:
                return {'message':'Token is invalid.'},403
            

        if not token:
            return {'message':'Token is missing or nor found'}
        
        if data:
            pass
        return f(*args, **kwargs)
    
    return decorated

api = Blueprint('api',__name__)
post1=Api(app=api,doc='/docs',version='1.4',title='AMS',authorizations=authorizations)

CORS(api,resources={r"/api/*":{"origins":"*"}})

uploader = post1.parser()
uploader.add_argument('file',location='files',type=FileStorage,required=False,help="You must parse a file")

uploader.add_argument('name',location='form',type=str,required=False,help="Name cannot be blank")



post_space= post1.namespace('/api/post',\
                       description="All routes under this section of the documentation are the open routes bot can perform\
                        CRUD action on the application",\
                            path='/v1/')


user_data = post_space.model('user_data',{
    "id":fields.Integer(required=False,default="",description="Identity"),
    "username":fields.String(required=False,default="",description="Username"),
    "email":fields.String(required=False,default="",description="Email"),
    "avatar_url":fields.String(required=False,default="",description="avatar"),
    "about_me":fields.String(required=False,default="",description="about me"),
    "last_seen":fields.String(required=False,default="",description="last seen"),
    "first_seen":fields.String(required=False,default="",description="last seen"),
})

post_data = post_space.model('post_data',{
    "text":fields.String(required=False,default="",description="Content"),
    "timestamp":fields.String(required=False,default="",description="Time"),
    "author":fields.Nested(user_data),
})


@post_space.doc(
    security='KEY',
    params={
            'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
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

@post_space.route('/post/create/')
class create(Resource):
    @token_required
    @post_space.expect(post_data)
    def post(self):
        token=request.headers['Authorization']
        data =jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user=User.query


@post_space.doc(
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

@post_space.route('/posts')
class all(Resource):
    @token_required
    def get(self):
        if request.args:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 6))
        else:
            page=1
            per_page=6

        
        #token=request.headers['Authorization']
        #data =jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        posts_=Post.query.paginate(page=page,per_page=per_page)
        print(posts_.items)
        return{
            "results":marshal(posts_.items,post_data),
            "pagination": {
                "page":page,
                "limit": per_page,
                "total": posts_.total
            }
        }


@post_space.doc(
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

@post_space.route('/users/<int:id>/posts')
class users_all_posts(Resource):
    @token_required
    def get(self,id):
        if request.args:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 6))
        else:
            page=1
            per_page=6

        
        #token=request.headers['Authorization']
        #data =jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        posts_=User.query.filter_by(id=id).first().posts.paginate(page=page,per_page=per_page)
        print(posts_.items)
        return{
            "results":marshal(posts_.items,post_data),
            "pagination": {
                "page":page,
                "limit": per_page,
                "total": posts_.total
            }
        }