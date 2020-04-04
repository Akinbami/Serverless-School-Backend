from flask import Flask, jsonify, request
from flask_jwt_extended import (
                                    JWTManager, 
                                    jwt_required, 
                                    create_access_token,
                                    get_jwt_identity
                                )

from app import app


jwt = JWTManager(app)



@jwt.unauthorized_loader
def no_authentication_code(e):
    return jsonify({
        'status': 401,
        'msg': f'{e}'
    }), 401


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401



@app.route("/")
# @hawk.auth_required
def hello():
    return "Hello World!"

@app.route('/api/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'opera' or password != 'opera':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    expires = timedelta(days=7)
    access_token = create_access_token(identity=username, expires_delta=expires)
    return jsonify(access_token=access_token), 200


@app.route('/api/sms/send', methods=["POST"])
@jwt_required
def send():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    delivery_status_callback_url = "https://fcxuwnhr41.execute-api.us-east-2.amazonaws.com/dev/api/sms/dlr_callback"


    # getting data
    data = json.loads(request.data)
    print(data)
    phone_number = data.get("msidn")
    network = data.get("network")   #(e.g 9mobile Airtel mtn)
    message = data.get("message")
    
    # sending message to user
    print("sending sms")
    sms_response = send_sms(phone_number,message,network,delivery_status_callback_url)

    # saving message
    message_instance = Message(content=message, receiver=phone_number, status=sms_response.status_code, response_message=sms_response.text  )
    db.session.add(message_instance)
    db.session.commit()

    return jsonify(message=sms_response.text, statusCode=sms_response.status_code)
