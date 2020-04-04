from flask_restful import Resource,reqparse
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token, 
                                jwt_required, 
                                jwt_refresh_token_required, 
                                get_jwt_identity, 
                                get_raw_jwt
                            )

from models import User,RevokedTokenModel, Post

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, help = 'This field cannot be blank', required = False)
parser.add_argument('password', type=str, help = 'This field cannot be blank', required = False)
parser.add_argument('title', type=str, help = 'This field cannot be blank', required = False)
parser.add_argument('content', type=str, help = 'This field cannot be blank', required = False)
parser.add_argument('puid', type=int, help = 'This field cannot be blank', required = False)
parser.add_argument('is_published', type=bool, help = 'This is the flag that indicates if a post should be published', required = False)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        if User.find_by_username(data['username']):
          return {'message': 'User {} already exists'. format(data['username'])}

        new_user = User(
            username = data['username'],
            password = User.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created'.format( data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = User.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials'}
      
      
class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
      
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
      
      
class AllUsers(Resource):
    def get(self):
        return User.return_all()
    
    def delete(self):
        return User.delete_all()


class CreatePost(Resource):
    def post(self):
        data = parser.parse_args()
        print(data)
        if Post.find_by_title(data['title']):
          return {'message': 'Post {} already exists'. format(data['title'])}

        new_post = Post(
            title = data['title'],
            content = data['content'],
            puid = data['puid'],
            is_published = data['is_published']
        )

        try:
            p = new_post.save_to_db()
            print(p)
            return {
                'message': 'Post {} was created'.format( data['title'])
            }
        except:
            return {'message': 'Something went wrong'}, 500


class AllPosts(Resource):
    def get(self):
        return Post.return_all()
    
    def delete(self):
        return Post.delete_all()


class PostDetail(Resource):
    def get(self,slug):
        return Post.find_by_title(slug)

    def patch(self, slug):
        post = Post.query.find_by_title(slug)

        if 'title' in request.json:
            post.title = request.json['title']
        if 'content' in request.json:
            post.content = request.json['content']
        if 'is_published' in request.json:
            post.content = request.json['is_published']

        return post.update_to_db()
    
    def delete(self):
        return Post.delete_all()
      
      
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }