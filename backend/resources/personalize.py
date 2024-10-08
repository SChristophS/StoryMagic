# resources/personalize.py

from flask_restful import Resource, reqparse
from flask import request
from utils.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.personalized_story import PersonalizedStory
from datetime import datetime
import logging
from bson.objectid import ObjectId
from utils.validations import is_valid_object_id, is_valid_name

class UserStories(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        try:
            stories_cursor = db.personalized_stories.find({'user_id': current_user_id})
            stories = [PersonalizedStory(s).to_dict() for s in stories_cursor]
            logging.debug(f"Personalized stories retrieved for user {current_user_id}")
            return stories, 200
        except Exception as e:
            logging.error(f"Error retrieving personalized stories: {e}")
            return {'message': 'Error retrieving personalized stories'}, 500

class DeletePersonalizedStory(Resource):
    @jwt_required()
    def delete(self, personalized_story_id):
        current_user_id = get_jwt_identity()
        if not is_valid_object_id(personalized_story_id):
            logging.warning(f"Invalid personalized story ID: {personalized_story_id}")
            return {'message': 'Invalid personalized story ID'}, 400
        try:
            result = db.personalized_stories.delete_one({
                '_id': ObjectId(personalized_story_id),
                'user_id': current_user_id
            })
            if result.deleted_count == 0:
                logging.warning(f"Personalized story not found or access denied: {personalized_story_id}")
                return {'message': 'Personalized story not found or access denied'}, 404
            logging.debug(f"Personalized story deleted: {personalized_story_id}")
            return {'message': 'Personalized story deleted successfully'}, 200
        except Exception as e:
            logging.error(f"Error deleting personalized story: {e}")
            return {'message': 'Error deleting personalized story'}, 500
            
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

        # ... Validierungscode ...

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




class PersonalizedStoryDetail(Resource):
    @jwt_required()
    def get(self, personalized_story_id):
        current_user_id = get_jwt_identity()
        if not is_valid_object_id(personalized_story_id):
            logging.warning(f"Invalid personalized story ID: {personalized_story_id}")
            return {'message': 'Invalid personalized story ID'}, 400
        try:
            story_data = db.personalized_stories.find_one({
                '_id': ObjectId(personalized_story_id),
                'user_id': current_user_id
            })
            if not story_data:
                logging.warning(f"Personalized story not found or access denied: {personalized_story_id}")
                return {'message': 'Personalized story not found'}, 404
            personalized_story = PersonalizedStory(story_data)
            logging.debug(f"Personalized story retrieved: {personalized_story.to_dict()}")
            return personalized_story.to_dict(), 200
        except Exception as e:
            logging.error(f"Error retrieving personalized story: {e}")
            return {'message': 'Error retrieving personalized story'}, 500

    @jwt_required()
    def delete(self, personalized_story_id):
        current_user_id = get_jwt_identity()
        if not is_valid_object_id(personalized_story_id):
            logging.warning(f"Invalid personalized story ID: {personalized_story_id}")
            return {'message': 'Invalid personalized story ID'}, 400
        try:
            result = db.personalized_stories.delete_one({
                '_id': ObjectId(personalized_story_id),
                'user_id': current_user_id
            })
            if result.deleted_count == 0:
                logging.warning(f"Personalized story not found or access denied: {personalized_story_id}")
                return {'message': 'Personalized story not found or access denied'}, 404
            logging.debug(f"Personalized story deleted: {personalized_story_id}")
            return {'message': 'Personalized story deleted successfully'}, 200
        except Exception as e:
            logging.error(f"Error deleting personalized story: {e}")
            return {'message': 'Error deleting personalized story'}, 500
