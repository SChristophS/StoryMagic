# models/personalized_story.py

from bson.objectid import ObjectId
from datetime import datetime

class PersonalizedStory:
    def __init__(self, data):
        self.id = str(data.get('_id', ''))
        self.story_id = data.get('story_id', '')
        self.personal_data = data.get('personal_data', {})
        self.user_images = data.get('user_images', [])
        self.created_at = data.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'personal_data': self.personal_data,
            'user_images': self.user_images,
            'created_at': self.created_at
        }
