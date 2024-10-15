# JSON Buch Editor

## **Beschreibung**

Der JSON Buch Editor ist ein vielseitiges Tool zur Erstellung und Bearbeitung von Büchern im JSON-Format. Es bietet sowohl eine grafische Benutzeroberfläche (GUI) für interaktive Bearbeitungen als auch einen Headless-Modus für automatisierte Prozesse wie die Erstellung von kombinierten JPG-Bildern.

## **Funktionen**

- **GUI-Modus:**
  - Öffnen, Bearbeiten und Speichern von JSON-Buchdateien.
  - Hinzufügen von Textelementen und Bildelementen auf den Buchseiten.
  - Navigieren zwischen den Seiten.
  - Anpassen der Buch-Einstellungen (Titel, Beschreibung, Autor, Illustrator, Seitenauflösung, Coverbild).
  
- **Headless-Modus:**
  - Automatisiertes Rendern von JSON-Buchdateien zu kombinierten JPG-Bildern.
  - Ideal für die Integration in Skripte oder automatisierte Workflows.

## **Installation**

1. **Klonen oder Herunterladen des Repositorys:**

   ```bash
   git clone https://github.com/IhrBenutzername/JSONBuchEditor.git
Navigieren Sie in das Projektverzeichnis:

bash
Code kopieren
cd JSONBuchEditor
Erstellen und Aktivieren einer Virtuellen Umgebung:

bash
Code kopieren
python -m venv venv
venv\Scripts\activate
Installieren der Abhängigkeiten:

bash
Code kopieren
pip install -r requirements.txt
Builden der ausführbaren Datei:

Führen Sie das Batch-Skript aus, um die .exe-Datei zu erstellen:

batch
Code kopieren
build.bat
Nach erfolgreichem Ausführen finden Sie die JSONBuchEditor.exe im dist-Ordner.