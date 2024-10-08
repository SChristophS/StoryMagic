# resources/generate_pdf.py

from flask_restful import Resource
from flask import current_app, send_file, abort
from utils.database import db
from models.personalized_story import PersonalizedStory
from models.story import Story
from bson.objectid import ObjectId
import logging
import os
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

class GeneratePDF(Resource):
    def get(self, personalized_story_id):
        if not ObjectId.is_valid(personalized_story_id):
            logging.warning(f"Invalid personalized story ID: {personalized_story_id}")
            return {'message': 'Invalid personalized story ID'}, 400
        try:
            # Hole die personalisierte Geschichte
            p_story_data = db.personalized_stories.find_one({'_id': ObjectId(personalized_story_id)})
            if not p_story_data:
                logging.warning(f"Personalized story not found: {personalized_story_id}")
                return {'message': 'Personalized story not found'}, 404
            personalized_story = PersonalizedStory(p_story_data)
            
            # Hole die ursprüngliche Geschichte
            story_data = db.stories.find_one({'_id': ObjectId(personalized_story.story_id)})
            if not story_data:
                logging.warning(f"Story not found: {personalized_story.story_id}")
                return {'message': 'Story not found'}, 404
            story = Story(story_data)
            
            # Render das HTML-Template
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('pdf_template.html')
            html_out = template.render(
                story=story,
                personal_data=personalized_story.personal_data,
                user_images=personalized_story.user_images
            )
            
            # Generiere das PDF
            pdf_filename = f"{personalized_story_id}.pdf"
            pdf_path = os.path.join('static', 'uploads', pdf_filename)
            HTML(string=html_out).write_pdf(pdf_path)
            logging.debug(f"PDF generated at: {pdf_path}")
            return {'pdf_path': pdf_path}, 200
        except Exception as e:
            logging.error(f"Error generating PDF: {e}")
            return {'message': 'Error generating PDF'}, 500

class DownloadPDF(Resource):
    def get(self, personalized_story_id):
        pdf_filename = f"{personalized_story_id}.pdf"
        pdf_path = os.path.join('static', 'uploads', pdf_filename)
        if not os.path.exists(pdf_path):
            logging.warning(f"PDF not found: {pdf_path}")
            return {'message': 'PDF not found'}, 404
        try:
            return send_file(pdf_path, as_attachment=True, attachment_filename=pdf_filename)
        except Exception as e:
            logging.error(f"Error sending PDF: {e}")
            abort(500, 'Error sending PDF')
