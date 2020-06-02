from flask import Flask,jsonify

from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
# from flask_rest_jsonapi import Api




import json

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://smartpy:Smartpy2020@smartpy-db.cerkzqsx9z8g.us-east-2.rds.amazonaws.com/abc"
app.config["SECRET_KEY"] = "hsbdoun3782ndyvbisjh82boindwyb"

app.config["JWT_SECRET_KEY"] = "dkfjhbniuwebvuiybweouhdihnybdwiuhowipeojwqoihq27hiu3hndun3789"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.now() + timedelta(days = 1)
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


CORS(app)

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint

import views, models, resources

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401
    
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api.add_resource(resources.UserRegistration, '/api/register')
api.add_resource(resources.UserLogin, '/api/login')
api.add_resource(resources.UserList, '/api/users')
api.add_resource(resources.UserDetail, '/api/users/<public_id>')
api.add_resource(resources.SecretResource, '/api/secret')


# api.add_resource(resources.UserLogoutAccess, '/api/logout/access')
# api.add_resource(resources.UserLogoutRefresh, '/api/logout/refresh')
# api.add_resource(resources.TokenRefresh, '/api/token/refresh')

# User api
# api.route(resources.UserList, 'user_list', '/api/users')
# api.route(resources.UserDetail, 'user_detail', '/api/users/<int:id>')
# api.route(resources.UserRelationship, 'user_posts', '/api/users/<int:id>/relationships/posts')


# post Api
# api.route(resources.PostList, 'post_list', '/api/posts')
# api.route(resources.PostDetail, 'post_detail', '/api/posts/<int:id>')
# api.route(resources.PosrRelationship, 'post_user', '/api/posts/<int:id>/relationships/order')
api.add_resource(resources.BlogList, '/api/posts')
api.add_resource(resources.Blog, '/api/posts/<int:id>')


# image Api
api.add_resource(resources.UploadImage, '/api/image/upload')

# contact API
api.add_resource(resources.ContactForm, '/api/contacts')
api.add_resource(resources.ContactDetail, '/api/contacts/<int:id>')

# testimony API
api.add_resource(resources.Testimony, '/api/testimonies')
api.add_resource(resources.TestimonialDetail, '/api/testimonies/<int:id>')

# subscription API
api.add_resource(resources.Subscribe, '/api/subscriptions')

# statistics API
api.add_resource(resources.Statistics, '/api/statistics')











