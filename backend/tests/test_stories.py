# tests/test_stories.py

import unittest
from app import app
from unittest.mock import patch
from bson.objectid import ObjectId

class TestStories(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    @patch('resources.stories.db')
    def test_get_stories_success(self, mock_db):
        mock_db.stories.find.return_value = [
            {'_id': ObjectId(), 'title': 'Geschichte 1', 'description': 'Beschreibung 1', 'cover_image': 'cover1.jpg'},
            {'_id': ObjectId(), 'title': 'Geschichte 2', 'description': 'Beschreibung 2', 'cover_image': 'cover2.jpg'}
        ]
        response = self.app.get('/api/stories')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Geschichte 1', str(response.data))
    
    @patch('resources.stories.db')
    def test_get_stories_failure(self, mock_db):
        mock_db.stories.find.side_effect = Exception('Database error')
        response = self.app.get('/api/stories')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error retrieving stories', str(response.data))
    
    @patch('resources.stories.db')
    def test_get_story_detail_success(self, mock_db):
        story_id = str(ObjectId())
        mock_db.stories.find_one.return_value = {
            '_id': ObjectId(story_id),
            'title': 'Geschichte 1',
            'description': 'Beschreibung 1',
            'cover_image': 'cover1.jpg',
            'scenes': []
        }
        response = self.app.get(f'/api/stories/{story_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Geschichte 1', str(response.data))
    
    def test_get_story_detail_invalid_id(self):
        response = self.app.get('/api/stories/invalid_id')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid story ID', str(response.data))
