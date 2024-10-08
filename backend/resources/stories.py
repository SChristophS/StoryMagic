# resources/stories.py

from flask_restful import Resource
from flask import request 
from utils.database import db
from models.story import Story
import logging
from bson.objectid import ObjectId
from flask import abort
from utils.validations import is_valid_object_id

class StoriesList(Resource):
    def get(self):
        role = request.args.get('role')
        child_age = request.args.get('childAge', type=int)
        query = {}
        if role:
            query['roles'] = role
        if child_age is not None:
            query['ageGroup'] = child_age
        try:
            logging.debug(f"Querying books with filters: {query}")
            # Inkludiere 'scenes' im Abfrageergebnis
            stories_cursor = db.stories.find(query, {'title': 1, 'description': 1, 'coverImage': 1, 'scenes': 1})
            stories = [Story(s).to_dict() for s in stories_cursor]
            logging.debug(f"Number of stories retrieved: {len(stories)}")
            logging.debug(f"Stories data: {stories}")
            return stories, 200
        except Exception as e:
            logging.error(f"Error retrieving stories: {e}")
            abort(500, 'Error retrieving stories')


class StoryDetail(Resource):
    def get(self, story_id):
        if not is_valid_object_id(story_id):
            logging.warning(f"Invalid story ID: {story_id}")
            abort(400, 'Invalid story ID')
        try:
            logging.debug(f"Looking for story with ID: {story_id}")
            # Inkludiere 'scenes' im Abfrageergebnis
            story_data = db.books.find_one({'_id': ObjectId(story_id)}, {'title': 1, 'description': 1, 'coverImage': 1, 'scenes': 1})
            if not story_data:
                logging.warning(f"Story not found: {story_id}")
                abort(404, 'Story not found')
            story = Story(story_data)
            logging.debug(f"Story retrieved: {story.to_dict()}")
            return story.to_dict(), 200
        except Exception as e:
            logging.error(f"Error retrieving story: {e}")
            abort(500, 'Error retrieving story')
