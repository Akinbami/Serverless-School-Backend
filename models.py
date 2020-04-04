from flask_migrate import Migrate, MigrateCommand
from flask_marshmallow import Marshmallow
from passlib.hash import pbkdf2_sha256 as sha256

from datetime import timedelta, datetime as dt
import datetime
import random

from app import app,db

ma = Marshmallow(app)
migrate = Migrate(app,db)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    # messages = db.relationship('Message', backref="sender", lazy=True)
    date_registered = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
        
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
       return cls.query.filter_by(username = username).first()


    @classmethod
    def return_all(cls):
        queryset = cls.query.all()
        users = users_schema.dump(queryset)
        return users

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(1000))
    puid = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save_to_db(self):
        db.session.commit();
        return post_schema.dump(self)

    @classmethod
    def find_by_title(cls, title):
       post =  cls.query.filter_by(title = title).first()
       return post_schema.dump(post)

    @classmethod
    def return_all(cls):
        queryset = cls.query.all()
        posts = posts_schema.dump(queryset)
        return posts


    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')
    # messages = ma.Nested(MessageSchema)

class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'is_published', 'date_posted', 'date_updated')
    user = ma.Nested(UserSchema)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


post_schema = PostSchema()
posts_schema = PostSchema(many=True)