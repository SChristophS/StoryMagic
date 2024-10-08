# app.py

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from config import Config
from utils.logging_config import configure_logging
from resources.stories import StoriesList, StoryDetail
from resources.personalize import PersonalizeStory, PersonalizedStoryDetail
from resources.upload import UploadImage
# from resources.generate_pdf import GeneratePDF, DownloadPDF

app = Flask(__name__)
app.config.from_object(Config)

# Temporäres Zulassen aller Origins zum Debuggen
CORS(app)

api = Api(app)

# Logging konfigurieren
configure_logging(app.config['DEBUG'])

# API-Ressourcen hinzufügen
api.add_resource(StoriesList, '/api/stories')
api.add_resource(StoryDetail, '/api/stories/<string:story_id>')
api.add_resource(PersonalizeStory, '/api/personalize')
api.add_resource(PersonalizedStoryDetail, '/api/personalized-story/<string:personalized_story_id>')
api.add_resource(UploadImage, '/api/upload-image')
# api.add_resource(GeneratePDF, '/api/generate-pdf/<string:personalized_story_id>')
# api.add_resource(DownloadPDF, '/api/download-pdf/<string:personalized_story_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=49158, debug=True)
