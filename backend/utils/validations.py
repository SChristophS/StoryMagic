# utils/validations.py

import re
from bson.objectid import ObjectId
from flask import current_app

def is_valid_name(name):
    return bool(name and name.strip())

def is_valid_object_id(oid):
    return ObjectId.is_valid(oid)

def allowed_file(filename):
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
