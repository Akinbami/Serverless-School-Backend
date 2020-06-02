from flask import request,make_response,jsonify
from flask_restful import Resource,reqparse,abort
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token, 
                                jwt_required, 
                                jwt_refresh_token_required, 
                                get_jwt_identity, 
                                get_raw_jwt
                            )

from sqlalchemy.orm.exc import NoResultFound
from slugify import slugify

from datetime import timedelta, datetime
import requests
import json
import uuid
import boto3
import logging
from botocore.client import Config

from io import BytesIO
import os

from models import User, Post,Contact,Subscription,Testimonial
from utils import create_presigned_url,send_email
      
def abort_if_blog_doesnt_exist(id):
    blog_item = Post.get_one(id)
    if not blog_item:
        abort(404, message="Blog Post {} doesn't exist".format(id))

def abort_if_user_doesnt_exist(public_id):
    user = User.get_one(public_id)
    if not user:
        abort(404, message="User {} doesn't exist".format(public_id))

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        password = User.generate_hash(data['password'])
        public_id = str(uuid.uuid4())

        # creating the user instance
        new_user = User(public_id=public_id,username=data['username'],email=data['email'],is_admin=data['is_admin'],password=password)
        user = new_user.save_to_db()

        return {"status": "Ok","data":user}

    def get(self):
        return {'hello': 'world'}

class UserLogin(Resource):
    def post(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login Required!'})

        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login Required!'})

        verify_user = User.verify_hash(auth.password,user.password)
        if verify_user:
            expires = timedelta(days=7)
            access_token = create_access_token(identity = auth.username,expires_delta=expires)
            refresh_token = create_refresh_token(identity = auth.username)
            return {
                'status': verify_user,
                'message': 'Logged in as {}'.format(user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials',"status": verify_user}

        
    def get(self):
        return {'hello': 'world'}
class UserLogout(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return jsonify({"msg": "Successfully logged out"}), 200

class UserList(Resource):
    def get(self):
        return User.return_all()

class UserDetail(Resource):
    def get(self, public_id):
        abort_if_user_doesnt_exist(public_id)
        return User.get_one(public_id)

    def delete(self, public_id):
        abort_if_user_doesnt_exist(public_id)
        User.delete_one(public_id)
        return '', 204

    def patch(self, public_id):
        data = request.get_json()
        user = User.query.get_or_404(public_id)

        # updating post
        if "username" in data:
            user.username = data['username']
        if "email" in data:
            user.email = data['email']
        if "is_admin" in data:
            user.is_admin = data['is_admin']

        update_response = user.update_db()


        return update_response, 201

# User page authorization
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'valid': True
        }
        
# Blog
# shows a single blog item and lets you delete a blog item
class Blog(Resource):
    def get(self, id):
        abort_if_blog_doesnt_exist(id)
        return Post.get_one(id)

    def delete(self, id):
        abort_if_blog_doesnt_exist(id)
        Post.delete_one(id)
        return {"status":200,"message":f"Post {id} deleted"}
        # try:
        #     Post.delete_one(id)
        #     return {"status":200,"message":f"Post {id} deleted"}
        # except:
        #     return {"status":500,"message":f"something went wrong with deleting Post {id}"}

    def put(self, id):
        data = request.get_json()
        post = Post.query.get_or_404(id)

        print("This is the raw data ",data)
        print("This is the blog item ",post)

        # updating post
        if "title" in data:
            post.title = data['title']
        if "content" in data:
            post.content = data['content']
        if "is_published" in data:
            post.is_published = data['is_published']
        if "category" in data:
            post.category = data['category']
        if "draft" in data:
            post.draft = True if data['draft']=="on" else False
        if "image_url" in data:
            post.image_url = data['image_url']

        post.date_updated = str(datetime.today())
        update_response = post.update_db()


        return update_response


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class BlogList(Resource):
    def get(self):
        return Post.return_all()

    @jwt_required
    def post(self):
        args = request.get_json()
        print(args)
        title = args.get('title')
        content = args.get('content')
        is_published = args.get('is_published')
        category = args.get('category')
        draft = True if args.get('is_draft')=="on" else False
        image = args.get('image_url')
        slug = slugify(title)

        auth_user = get_jwt_identity()
        if auth_user:
            user = User.query.filter_by(username=auth_user).first()
        else:
            abort(404, message="Unauthorized user {}".format(auth_user))

        print(user)

        blog_item = Post.find_by_title(title)
        if blog_item:
            abort(404, message="Blog Post {} already exist".format(title))


        post = Post(title=title, slug=slug, content=content, is_published=is_published,puid=user.id,category=category, is_draft=draft, image_url=image)
        post_response = post.save_to_db()
        return {"status": "Ok","data": post_response}, 201

# ImageUpload
# api to accept images and upload to s3
class UploadImage(Resource):
    @jwt_required
    def post(self):
        data = request.files
        image = data.get("image")
        print(image)
        print(dir(image))
        print(image.content_type)
        print(image.filename)
        print(image.name)
        print(image.mimetype)
        print(image.mimetype_params)
        print(image.stream)

        

        # s3 = boto3.resource('s3',
        #                     aws_access_key_id=os.environ["ACCESS_KEY"],
        #                     aws_secret_access_key=os.environ["SECRETE_KEY"],
        #                     config=Config(signature_version="s3v4"))
        bucket = os.environ["BUCKET"]
        region = os.environ["REGION"]
        key = image.filename.split('.')[0] #"".join(str(uuid.uuid4()).split("-"))
        extension = image.filename.split('.')[-1]
        full_file_name = '.'.join([key,extension])
        # opening a file
        f = open('Machine.jpg', 'r+')
        jpgdata = f.read()
        # print("extension ",extension)
        # print(type(key))
        # obj = s3.Bucket(bucket).put_object(Key=full_file_name,Body=image, ContentType=image.content_type)
        # print(obj)

        # image_url = f"https://s3-{region}.amazonaws.com/{bucket}/{'.'.join([key,extension])}"
        # return {"status": "Ok","url": image_url}, 201
        response = create_presigned_url(bucket, 'Machine.jpg')

        

        files = {'file': ('Machine.jpg', jpgdata)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
        # If successful, returns HTTP status code 204
        print("response fields ",response['fields'])
        logging.info(f'File upload HTTP status code: {http_response.status_code}')

        print(dir(http_response))
        print(http_response.json)
        # print(http_response.data)
        print(http_response.text)



        return response


class ContactForm(Resource):
    def get(self):
        return Contact.return_all()
    def post(self):
        data = json.loads(request.data)
        print(data)
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        phone = data.get("phone")
        message = data.get("message")
        # network = check_telco(phone[1:])

        contact_instance = Contact(phone=phone,email=email,name=name,subject=subject,message=message)
        contact = contact_instance.save_to_db()
        if contact:
            # sending sms
            # sms_message = "Thank you for registering for the event. We will send you a reminder on the day, so you don't miss out. Love Hive"
            # sms_res = send_sms(phone, sms_message, network, STATUS_URL)
            # print("sms response to user", sms_res)
            # print("successfully saved")

            # sending email
            print("sending email...")
            destination = "info@schoolofabi.com"
            email_message = f"{message}\n\nName: {name}\nEmail: {email}\nPhone Number: {phone}"
            subject = subject.upper()
            send_email(subject,destination,email_message)
            
            return jsonify(status="ok",data=data,error=False)
        else:
            print("an error occured....")
            return jsonify(status="ok",data=data,error=True)


class ContactDetail(Resource):
    def get(self, id):
        abort_if_user_doesnt_exist(id)
        return Contact.get_one(id)

    def delete(self, id):
        abort_if_user_doesnt_exist(id)
        Contact.delete_one(id)
        return '', 204

    def patch(self, id):
        data = request.get_json()
        contact = Contact.query.get_or_404(id)

        # updating post
        if "name" in data:
            contact.name = data['name']
        if "email" in data:
            contact.email = data['email']
        if "subject" in data:
            contact.subject = data['subject']

        update_response = contact.update_db()


        return update_response, 201

class Statistics(Resource):
    def get(self):
        res = {
            "contacts": len(Contact.return_all().data),
            "subscriptions": len(Subscription.return_all().data),
            "testimonies": len(Testimonial.return_all().data),
            "users": len(User.return_all().data),
        }
        return res

class Subscribe(Resource):
    def get(self):
        return User.return_all()
    def post(self):
        data = json.loads(request.data)
        print(data)
        email = data.get("email")

        if Subscription.query.filter_by(email=email).first():
            print("already subscribed.")
            return jsonify(status="ok",data="Already subscribed",error=True)

        subscription_instance = Subscription(email=email)
        subscription = subscription_instance.save_to_db()
        if subscription:
            # sending sms
            # sms_message = "Thank you for registering for the event. We will send you a reminder on the day, so you don't miss out. Love Hive"
            # sms_res = send_sms(phone, sms_message, network, STATUS_URL)
            # print("sms response to user", sms_res)
            # print("successfully saved")

            # sending email
            print("sending email...")
            destination = "info@schoolofabi.com"
            email_message = f"Email: {email}"
            subject = "SUBSCRIPTION"
            send_email(subject,destination,email_message)
            
            return jsonify(status="ok",data=data,error=False)
        else:
            print("an error occured....")
            return jsonify(status="ok",data=data,error=True)


class Testimony(Resource):
    def get(self):
        return Testimonial.return_all()
    def post(self):
        data = json.loads(request.data)
        print(data)
        name = data.get("name")
        occupation = data.get("occupation")
        message = data.get("message")
        is_active = data.get("is_active")


        testimonial_instance = Testimonial(name=name, occupation=occupation, message=message,is_active=is_active)
        testimonial = testimonial_instance.save_to_db()
        if testimonial:
            print("testimonial created")
            return jsonify(status="ok",data=data,error=False)
        else:
            print("an error occured....")
            return jsonify(status="ok",data=data,error=True)

class TestimonialDetail(Resource):
    def get(self, id):
        # abort_if_user_doesnt_exist(id)
        return Testimonial.get_one(id)

    def delete(self, id):
        # abort_if_user_doesnt_exist(id)
        Testimonial.delete_one(id)
        return {"status":200,"message":f"Testimony {id} deleted"}

    def patch(self, id):
        data = request.get_json()
        testimonial = Testimonial.query.get_or_404(id)

        # updating post
        if "name" in data:
            testimonial.name = data['name']
        if "message" in data:
            testimonial.message = data['message']
        if "occupation" in data:
            testimonial.subject = data['occupation']

        update_response = testimonial.update_db()


        return update_response, 201


    

