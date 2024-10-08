# Personalisierte Geschichtenbücher - Backend

## Übersicht

Dies ist das Backend für die Anwendung "Personalisierte Geschichtenbücher". Es bietet API-Endpunkte zur Verwaltung von Geschichten, Personalisierung durch Nutzer, Bild-Uploads und PDF-Generierung.

## Voraussetzungen

- Python 3.8 oder höher
- MongoDB
- Virtuelle Umgebung (empfohlen)

## Installation

1. **Repository klonen**

   bash
   git clone https://github.com/dein-benutzername/personalized-books-backend.git
   cd personalized-books-backend


2. **Virtuelle Umgebung erstellen**
	python -m venv venv
	source venv/bin/activate  # Für Unix
	# oder
	venv\Scripts\activate  # Für Windows
	
3. **Abhängigkeiten installieren**
	pip install -r requirements.txt

4. **Konfiguration anpassen**
	Erstelle eine .env-Datei oder passe config.py an, um deine Datenbankverbindung und andere Einstellungen zu konfigurieren.	
	
5. **Ausführen der Anwendung**
	python app.py

6. **Ausführen der Tests**
	python -m unittest discover tests



## Ordnerstruktur
	app.py: Haupteinstiegspunkt der Anwendung
	config.py: Konfigurationsdatei
	models/: Datenmodelle
	resources/: API-Ressourcen
	utils/: Hilfsfunktionen (Datenbank, Validierungen, Logging)
	tests/: Unit Tests
	templates/: HTML-Templates für die PDF-Generierung
	static/uploads/: Ordner für hochgeladene Dateien und generierte PDFs
	
	
## Wichtige Endpunkte	
	Wichtige Endpunkte
	Geschichtenverwaltung

	GET /api/stories: Liste aller Geschichten
	GET /api/stories/<id>: Details einer Geschichte
	Personalisierung

	POST /api/personalize: Personalisierte Geschichte erstellen
	GET /api/personalized-story/<id>: Personalisierte Geschichte abrufen
	Bild-Upload

	POST /api/upload-image: Bild hochladen
	PDF-Generierung

	GET /api/generate-pdf/<id>: PDF generieren
	GET /api/download-pdf/<id>: PDF herunterladen