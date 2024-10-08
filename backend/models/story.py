# models/story.py

#from bson.objectid import ObjectId

# models/story.py

class Story:
    def __init__(self, data):
        self.id = str(data.get('_id'))
        self.title = data.get('title')
        self.description = data.get('description')
        self.cover_image = data.get('coverImage')
        self.scenes = data.get('scenes', [])
        # Füge weitere Felder nach Bedarf hinzu

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'coverImage': self.cover_image,
            'scenes': self.scenes,  # Stelle sicher, dass 'scenes' enthalten ist
            # Füge weitere Felder hinzu
        }
