# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import get_db
from werkzeug.utils import secure_filename
import base64
import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__, static_url_path='', static_folder='static')

CORS(app, resources={r"/api/*": {"origins": "*"}})


# Konfiguration
app.config['UPLOAD_FOLDER'] = 'uploads/images/'
app.config['PDF_FOLDER'] = 'uploads/pdfs/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Stelle sicher, dass die Upload-Ordner existieren
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Verbindung zur Datenbank herstellen
db = get_db()

# Hilfsfunktion zur Überprüfung der Dateierweiterung
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# API-Endpunkt zum Abrufen der Geschichten basierend auf Rolle und Alter
@app.route('/api/stories', methods=['GET'])
def get_stories():
    role = request.args.get('role')
    age = request.args.get('age', type=int)
    stories_collection = db['stories']

    query = {}
    if role:
        query['suitableRoles'] = role
    if age is not None:
        query['minAge'] = {'$lte': age}
        query['maxAge'] = {'$gte': age}

    stories = list(stories_collection.find(query))
    for story in stories:
        story['_id'] = str(story['_id'])  # ObjectId in String umwandeln

    return jsonify(stories), 200

# API-Endpunkt zum Hochladen des Bildes
@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'Kein Bild empfangen'}), 400

    try:
        # Base64-Daten extrahieren
        header, encoded = image_data.split(',', 1)
        file_ext = header.split(';')[0].split('/')[1]
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({'error': 'Ungültiges Bildformat'}), 400

        image_bytes = base64.b64decode(encoded)
        filename = secure_filename(f"{ObjectId()}.{file_ext}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Bild speichern
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        # Optional: Bild komprimieren oder validieren
        # with Image.open(file_path) as img:
        #     img = img.resize((800, 600))
        #     img.save(file_path)

        image_url = f"/{file_path}"

        return jsonify({'imageUrl': image_url}), 200

    except Exception as e:
        print('Fehler beim Hochladen des Bildes:', e)
        return jsonify({'error': 'Fehler beim Hochladen des Bildes'}), 500

# API-Endpunkt zum Aufgeben der Bestellung
@app.route('/api/place-order', methods=['POST'])
def place_order():
    data = request.get_json()

    required_fields = ['userName', 'childName', 'photo', 'storyId', 'orderData']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Fehlende Bestelldaten'}), 400

    orders_collection = db['orders']

    # Bestellung in der Datenbank speichern
    order = {
        'userName': data['userName'],
        'childName': data['childName'],
        'photo': data['photo'],
        'storyId': data['storyId'],
        'orderData': data['orderData'],
        'status': 'received'
    }
    order_id = orders_collection.insert_one(order).inserted_id

    # PDF erstellen
    pdf_filename = os.path.join(app.config['PDF_FOLDER'], f"{order_id}.pdf")
    create_pdf(order, pdf_filename)

    # Hier könntest du die Bestellung an den Druckdienstleister senden

    return jsonify({'success': True, 'orderId': str(order_id)}), 200

# Funktion zur PDF-Erstellung
def create_pdf(order, filename):
    try:
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Titel und Namen hinzufügen
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, order['userName'] + 's Geschichte für ' + order['childName'])

        # Bild hinzufügen
        image_data = order['photo']
        header, encoded = image_data.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{ObjectId()}.png")
        with open(image_filename, 'wb') as f:
            f.write(image_bytes)

        c.drawImage(image_filename, 100, height - 400, width=400, height=300)

        # Text der Geschichte hinzufügen (Dummy-Text)
        textobject = c.beginText(50, height - 450)
        textobject.setFont("Helvetica", 14)
        textobject.textLines("Dies ist eine personalisierte Geschichte für " + order['childName'] + ".\n\nViel Spaß beim Lesen!")

        c.drawText(textobject)
        c.save()

        # Temporäre Bilddatei löschen
        os.remove(image_filename)

        print('PDF erstellt:', filename)
    except Exception as e:
        print('Fehler beim Erstellen des PDFs:', e)

# Start der Anwendung
if __name__ == '__main__':
    app.run(debug=True)
