from flask_migrate import Migrate, MigrateCommand
from flask_marshmallow import Marshmallow

# from marshmallow_jsonapi import fields
# from marshmallow_jsonapi.flask import Schema, Relationship
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
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000),nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
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
        return user_schema.dump(self)

    def update_db(self):
        db.session.commit()
        return user_schema.dump(self)

    @classmethod
    def find_by_username(cls, username):
        user = cls.query.filter_by(username = username).first()
        return user_schema.dump(user)

    @classmethod
    def get_one(cls, public_id):
       user =  cls.query.filter_by(public_id=public_id).first()
       return user_schema.dump(user)

    @classmethod
    def delete_one(cls, public_id):
       user =  cls.query.filter_by(public_id=public_id).first()
       db.session.delete(user)
       db.session.comit()
       return user_schema.dump(user)


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
    slug = db.Column(db.String(200), nullable=False, default="blank")
    image_url = db.Column(db.String(200), nullable=False, default="blank")
    content = db.Column(db.Text)
    puid = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100), nullable=False, default="Uncategorized")
    is_draft = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return post_schema.dump(self)
        

    def update_db(self):
        db.session.commit();
        return post_schema.dump(self)

    @classmethod
    def find_by_title(cls, title):
        post =  cls.query.filter_by(title = title).first()
        if post:
            return post_schema.dump(post)
        else:
            return None

    @classmethod
    def get_one(cls, id):
       post =  cls.query.get_or_404(id)
       print(post)
       return post_schema.dump(post)

    @classmethod
    def delete_one(cls, id):
       post =  Post.query.get(id)
       print("deleted post ",post)
       db.session.delete(post)
       db.session.commit()

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


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False, default="")
    date_posted = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return contact_schema.dump(self)
        

    def update_db(self):
        db.session.commit();
        return contact_schema.dump(self)

    @classmethod
    def find_by_name(cls, name):
        contact = cls.query.filter_by(name = name).first()
        return contact_schema.dump(contact)

    @classmethod
    def get_one(cls, id):
       contact =  cls.query.filter_by(id=id).first()
       return contact_schema.dump(contact)

    @classmethod
    def delete_one(cls, id):
       contact =  cls.query.filter_by(id=id).first()
       db.session.delete(contact)
       db.session.commit()
       return contact_schema.dump(contact)


    @classmethod
    def return_all(cls):
        queryset = cls.query.all()
        contacts = contacts_schema.dump(queryset)
        return contacts

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return subscription_schema.dump(self)
        

    def update_db(self):
        db.session.commit();
        return subscription_schema.dump(self)

    @classmethod
    def return_all(cls):
        queryset = cls.query.all()
        subscriptions = subscriptions_schema.dump(queryset)
        return subscriptions

class Testimonial(db.Model):
    __tablename__ = "testimonial"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=str(dt.today()))
    date_updated = db.Column(db.DateTime, nullable=False, default=str(dt.today()))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return testimonial_schema.dump(self)
        

    def update_db(self):
        db.session.commit();
        return testimonial_schema.dump(self)

    @classmethod
    def get_one(cls, id):
       testimonial =  cls.query.filter_by(id=id).first()
       return testimonial_schema.dump(testimonial)

    @classmethod
    def delete_one(cls, id):
       testimonial =  cls.query.filter_by(id=id).first()
       db.session.delete(testimonial)
       db.session.commit()
       return testimonial_schema.dump(testimonial)

    @classmethod
    def return_all(cls):
        queryset = cls.query.all()
        return testimonials_schema.dump(queryset)


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


class PostSchema(ma.Schema):
    class Meta:
        fields = ("id","title","slug","content","is_published","image_url", "category","is_draft","puid","date_posted","_links")

    
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("blog", id="<id>"), "collection": ma.URLFor("bloglist")}
    )

class UserSchema(ma.Schema):
    posts = ma.Nested(PostSchema, many=True)
    class Meta:
        fields = ("id","public_id","username","email","is_admin","date_registered","_links")

    
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("userdetail", public_id="<public_id>"), "collection": ma.URLFor("userlist")}
    )

class ContactSchema(ma.Schema):
    class Meta:
        fields = ("id","name","phone","email","message","subject", "date_posted","_links")

    
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("contactdetail", id="<id>"), "collection": ma.URLFor("contactform")}
    )

class SubscriptionSchema(ma.Schema):
    class Meta:
        fields = ("id","email")

class TestimonialSchema(ma.Schema):
    class Meta:
        fields = ("id","name","occupation","message","is_active", "date_posted", "date_updated","_links")

    
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("testimonialdetail", id="<id>"), "collection": ma.URLFor("testimony")}
    )

# class UserSchema(Schema):
#     class Meta:
#         type_ = 'user'
#         self_view = 'user_detail'
#         self_view_kwargs = {'id': '<id>'}
#         self_view_many = 'user_list'

#     id = fields.Integer(as_string=True, dump_only=True)
#     username = fields.Str(required=True)
#     email = fields.Str(required=True)
#     password = fields.Str(required=True)

#     display_name = fields.Function(lambda obj: "{} <{}>".format(obj.email.upper(),obj.id))
#     posts = Relationship(self_view='user_pos',
#                              self_view_kwargs={'id': '<id>'},
#                              related_view='post_list',
#                              related_view_kwargs={'user_id': '<id>'},
#                              many=False,
#                              schema='PostSchema',
#                              type_='post')

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

subscription_schema = SubscriptionSchema()
subscriptions_schema = SubscriptionSchema(many=True)

testimonial_schema = TestimonialSchema()
testimonials_schema = TestimonialSchema(many=True)
