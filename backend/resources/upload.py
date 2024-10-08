# resources/upload.py

from flask_restful import Resource, reqparse
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from utils.validations import allowed_file
from datetime import datetime
from utils.database import db
import logging

class UploadImage(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return {'message': 'No file part'}, 400
        file = request.files['file']
        if file.filename == '':
            logging.warning("No selected file")
            return {'message': 'No selected file'}, 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Füge Benutzer-ID und Timestamp zum Dateinamen hinzu
            unique_filename = f"{current_user_id}_{int(datetime.utcnow().timestamp())}_{filename}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            logging.debug(f"File uploaded: {file_path}")
            # Speichere den Bildpfad in der Datenbank
            db.user_images.insert_one({
                'user_id': current_user_id,
                'file_path': file_path,
                'uploaded_at': datetime.utcnow()
            })
            return {'file_path': file_path}, 201
        else:
            logging.warning("File type not allowed")
            return {'message': 'File type not allowed'}, 400

