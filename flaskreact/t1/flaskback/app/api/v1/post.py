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
post1=Api(app=api,doc='/docs',version='1.4',title='AMS',authorizations=authorizations)

CORS(api,resources={r"/api/*":{"origins":"*"}})

uploader = post1.parser()
uploader.add_argument('file',location='files',type=FileStorage,required=False,help="You must parse a file")

uploader.add_argument('name',location='form',type=str,required=False,help="Name cannot be blank")



post_space= post1.Namespace('/api/post',\
                       description="All routes under this section of the documentation are the open routes bot can perform\
                        CRUD action on the application",\
                            path='/v1/')



post_data = post_space('post_data',{
    "content":fields.String(required=False,default="",description="Content"),
    "title":fields.String(required=False,default="",description="Title")
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