# config.py

import os

class Config:
    DEBUG = True
    TESTING = False
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://192.168.178.25:49155/')
    DATABASE_NAME = 'personalized_books'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
