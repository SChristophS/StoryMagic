# database.py

import logging
from pymongo import MongoClient, errors

class DatabaseManager:
    def __init__(self, host='192.168.178.25', port=49155, db_name='personalized_books', collection_name='stories'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.host, self.port, serverSelectionTimeoutMS=5000)
            # Überprüfen der Verbindung
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logging.info(f"Erfolgreich mit MongoDB verbunden: {self.host}:{self.port}, Datenbank: {self.db_name}, Sammlung: {self.collection_name}")
        except errors.ServerSelectionTimeoutError as err:
            logging.error(f"Fehler bei der Verbindung zu MongoDB: {err}")
            self.client = None
            self.db = None
            self.collection = None

    def get_all_stories(self):
        if self.collection is None:
            logging.error("Keine Verbindung zur MongoDB. Kann keine Geschichten abrufen.")
            return []
        try:
            return list(self.collection.find())
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Geschichten: {e}")
            return []

    def get_story_by_id(self, story_id):
        if self.collection is None:
            logging.error("Keine Verbindung zur MongoDB. Kann keine Geschichte abrufen.")
            return None
        try:
            return self.collection.find_one({"_id": story_id})
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Geschichte mit ID {story_id}: {e}")
            return None

    def save_story(self, story_data):
        try:
            if '_id' in story_data:
                result = self.collection.update_one({'_id': story_data['_id']}, {'$set': story_data})
            else:
                result = self.collection.insert_one(story_data)
            
            # Stellen Sie sicher, dass acknowledged True ist
            if result.acknowledged:
                logging.info("Geschichte erfolgreich gespeichert.")
            else:
                logging.error("Fehler beim Speichern der Geschichte.")
            return result.acknowledged
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Geschichte: {e}")
            return False


    def delete_story(self, story_id):
        if self.collection is None:
            logging.error("Keine Verbindung zur MongoDB. Kann keine Geschichte löschen.")
            return False
        try:
            result = self.collection.delete_one({"_id": story_id})
            if result.deleted_count > 0:
                logging.info(f"Geschichte mit ID {story_id} gelöscht.")
                return True
            else:
                logging.warning(f"Keine Geschichte mit ID {story_id} gefunden.")
                return False
        except Exception as e:
            logging.error(f"Fehler beim Löschen der Geschichte mit ID {story_id}: {e}")
            return False

    def update_settings(self, host, port, db_name, collection_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
        self.connect()
