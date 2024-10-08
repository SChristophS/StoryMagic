# resources/auth.py

from flask_restful import Resource, reqparse
from utils.database import db
from models.user import User
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import logging

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        if db.users.find_one({'username': username}):
            logging.warning(f"Username already exists: {username}")
            return {'message': 'Username already exists'}, 400

        password_hash = generate_password_hash(password)
        user = {'username': username, 'password_hash': password_hash}
        result = db.users.insert_one(user)
        logging.debug(f"User registered with ID: {result.inserted_id}")
        return {'message': 'User registered successfully'}, 201

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        user_data = db.users.find_one({'username': username})
        if not user_data:
            logging.warning(f"User not found: {username}")
            return {'message': 'Invalid username or password'}, 401

        user = User(user_data)
        if not user.check_password(password):
            logging.warning(f"Invalid password for user: {username}")
            return {'message': 'Invalid username or password'}, 401

        access_token = create_access_token(identity=user.id)
        logging.debug(f"User logged in: {username}")
        return {'access_token': access_token}, 200
