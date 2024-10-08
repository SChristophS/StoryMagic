# resources/personalize.py

from flask_restful import Resource, reqparse
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


class PersonalizeStory(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('story_id', required=True, help='Story ID is required')
        parser.add_argument('personal_data', type=dict, required=True, help='Personal data is required')
        parser.add_argument('user_images', type=list, location='json', required=False)
        args = parser.parse_args()
        
        story_id = args['story_id']
        personal_data = args['personal_data']
        user_images = args.get('user_images', [])
        
        if not is_valid_object_id(story_id):
            logging.warning(f"Invalid story ID: {story_id}")
            return {'message': 'Invalid story ID'}, 400
        if not is_valid_name(personal_data.get('child_name')):
            logging.warning("Invalid personal data: Missing child's name")
            return {'message': "Child's name is required"}, 400
        try:
            # Prüfe, ob die Geschichte existiert
            if not db.stories.find_one({'_id': ObjectId(story_id)}):
                logging.warning(f"Story not found: {story_id}")
                return {'message': 'Story not found'}, 404
            
            # Erstelle die personalisierte Geschichte
            personalized_story = {
                'user_id' : current_user_id,
                'story_id': story_id,
                'personal_data': personal_data,
                'user_images': user_images,
                'created_at': datetime.utcnow()
            }
            result = db.personalized_stories.insert_one(personalized_story)
            logging.debug(f"Personalized story created with ID: {result.inserted_id}")
            return {'personalized_story_id': str(result.inserted_id)}, 201
        except Exception as e:
            logging.error(f"Error creating personalized story: {e}")
            return {'message': 'Error creating personalized story'}, 500

class PersonalizedStoryDetail(Resource):
    def get(self, personalized_story_id):
        if not is_valid_object_id(personalized_story_id):
            logging.warning(f"Invalid personalized story ID: {personalized_story_id}")
            return {'message': 'Invalid personalized story ID'}, 400
        try:
            story_data = db.personalized_stories.find_one({'_id': ObjectId(personalized_story_id)})
            if not story_data:
                logging.warning(f"Personalized story not found: {personalized_story_id}")
                return {'message': 'Personalized story not found'}, 404
            personalized_story = PersonalizedStory(story_data)
            logging.debug(f"Personalized story retrieved: {personalized_story.to_dict()}")
            return personalized_story.to_dict(), 200
        except Exception as e:
            logging.error(f"Error retrieving personalized story: {e}")
            return {'message': 'Error retrieving personalized story'}, 500
