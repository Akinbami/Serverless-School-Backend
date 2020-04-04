from flask import Flask

from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager



import json

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://smartpy:Smartpy2020@smartpy-db.cerkzqsx9z8g.us-east-2.rds.amazonaws.com/abc"
app.config["JWT_SECRET_KEY"] = "my-abc-secret"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.now() + timedelta(days = 1)
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# CORS(app)

import views, models, resources


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api.add_resource(resources.UserRegistration, '/api/registration')
api.add_resource(resources.UserLogin, '/api/login')
api.add_resource(resources.UserLogoutAccess, '/api/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(resources.TokenRefresh, '/api/token/refresh')
api.add_resource(resources.AllUsers, '/api/users')
api.add_resource(resources.SecretResource, '/api/secret')


api.add_resource(resources.CreatePost, '/api/post/create')
api.add_resource(resources.AllPosts, '/api/posts')
api.add_resource(resources.PostDetail, '/api/posts/<string:slug>')




