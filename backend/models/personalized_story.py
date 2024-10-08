# models/personalized_story.py

class PersonalizedStory:
    def __init__(self, data):
        self.id = str(data.get('_id', ''))
        self.user_id = data.get('user_id', '')
        self.story_id = data.get('story_id', '')
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.scenes = data.get('scenes', [])
        self.personal_data = data.get('personal_data', {})
        self.created_at = data.get('created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'title': self.title,
            'description': self.description,
            'scenes': self.scenes,
            'personal_data': self.personal_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
