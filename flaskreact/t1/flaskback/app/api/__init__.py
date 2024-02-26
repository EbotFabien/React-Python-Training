from flask import Blueprint, url_for
from flask_restx import Api
from flask_cors import CORS
from .v1 import post_space,user_space,token_space

authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api=Blueprint('api',__name__,template_folder='../templates')

apisec = Api(app=api, doc='/docs', version='1.9.0', title='Test Blog.',
             description='This documentation contains all routes to access the Test Blog. \npip install googletransSome routes require authorization and can only be gotten \
    from the odaaay company', license='../LICENSE', license_url='www.blog.com', contact='leslie.etubo@gmail.com', authorizations=authorizations)

#CORS(api,resources={r"/api/*":{"origins":"*"}})

apisec.add_namespace(post_space)
apisec.add_namespace(user_space)
apisec.add_namespace(token_space)