# resources/personalize.py

from flask_restful import Resource
from flask import request
from utils.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.personalized_story import PersonalizedStory
from datetime import datetime
import logging
from bson.objectid import ObjectId
from utils.validations import is_valid_object_id, is_valid_name

class PersonalizeStory(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()

        story_id = data.get('story_id')
        personal_data = data.get('personal_data')
        user_images = data.get('user_images', {})  # Erwartet ein Dictionary

        if not isinstance(user_images, dict):
            user_images = {}

        if not is_valid_object_id(story_id):
            logging.warning(f"Invalid story ID: {story_id}")
            return {'message': 'Invalid story ID'}, 400
        if not is_valid_name(personal_data.get('child_name')):
            logging.warning("Invalid personal data: Missing child's name")
            return {'message': "Child's name is required"}, 400
        try:
            # Hole die ursprüngliche Geschichte
            original_story = db.stories.find_one({'_id': ObjectId(story_id)})
            if not original_story:
                logging.warning(f"Story not found: {story_id}")
                return {'message': 'Story not found'}, 404

            # personalisieren der Szenen
            personalized_scenes = []
            for index, scene in enumerate(original_story.get('scenes', [])):
                personalized_scene = scene.copy()

                # Bilder der Szene zuordnen
                if str(index) in user_images:
                    for img_elem in personalized_scene.get('imageElements', []):
                        img_elem['imageUrl'] = user_images[str(index)]
                personalized_scenes.append(personalized_scene)

            # Erstelle die personalisierte Geschichte
            personalized_story = {
                'user_id': current_user_id,
                'story_id': story_id,
                'title': original_story.get('title', ''),
                'description': original_story.get('description', ''),
                'scenes': personalized_scenes,
                'personal_data': personal_data,
                'created_at': datetime.utcnow()
            }
            result = db.personalized_stories.insert_one(personalized_story)
            logging.debug(f"Personalized story created with ID: {result.inserted_id}")
            return {'personalized_story_id': str(result.inserted_id)}, 201

        except Exception as e:
            logging.error(f"Error creating personalized story: {e}", exc_info=True)
            return {'message': 'Error creating personalized story'}, 500
