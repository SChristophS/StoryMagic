# resources/upload.py

from flask_restful import Resource, reqparse
from flask import request, current_app
import os
from werkzeug.utils import secure_filename
from utils.validations import allowed_file
import logging

class UploadImage(Resource):
    def post(self):
        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return {'message': 'No file part'}, 400
        file = request.files['file']
        if file.filename == '':
            logging.warning("No selected file")
            return {'message': 'No selected file'}, 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            logging.debug(f"File uploaded: {file_path}")
            return {'file_path': file_path}, 201
        else:
            logging.warning("File type not allowed")
            return {'message': 'File type not allowed'}, 400
