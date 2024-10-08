# tests/test_upload.py

import unittest
from app import app
from unittest.mock import patch
from io import BytesIO

class TestUpload(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    @patch('resources.upload.os')
    def test_upload_image_success(self, mock_os):
        mock_os.makedirs.return_value = True
        data = {
            'file': (BytesIO(b'my file contents'), 'test.jpg'),
        }
        response = self.app.post('/api/upload-image', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('file_path', response.get_json())
    
    def test_upload_image_no_file(self):
        response = self.app.post('/api/upload-image', content_type='multipart/form-data', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file part', str(response.data))
    
    def test_upload_image_invalid_file_type(self):
        data = {
            'file': (BytesIO(b'my file contents'), 'test.txt'),
        }
        response = self.app.post('/api/upload-image', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('File type not allowed', str(response.data))

if __name__ == '__main__':
    unittest.main()
