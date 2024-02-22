import json
from flask_restx import Namespace,Resource,fields,marshal,Api 
import jwt,os 
from flask_cors import CORS

from functools import wraps
from flask import request,Blueprint
from flask import current_app as app

from app.models import Post,User
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
            token = request.headers['Authorization']
            try:
                data=jwt.decode(token,app.config.get('SECRET_KEY'))
            except:
                return {'message':'Token is invalid.'},403
            

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
    "last_seen":fields.DateTime(required=False,default="",description="last seen"),
    "first_seen":fields.DateTime(required=False,default="",description="last seen"),
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
    #@token_required
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