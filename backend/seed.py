# seed.py
from pymongo import MongoClient

def seed_data():
    client = MongoClient('mongodb://192.168.178.25:49155/')
    db = client['storymagic']
    stories_collection = db['stories_collection']

    # Alte Daten löschen
    stories_collection.delete_many({})

    stories = [
        {
            'title': 'Das Abenteuer im Zauberwald',
            'description': 'Begleite dein Kind auf einem magischen Abenteuer.',
            'coverImage': 'http://localhost:5000/static/images/cover1.jpg',
            'suitableRoles': ['Oma', 'Opa', 'Mama', 'Papa'],
            'minAge': 3,
            'maxAge': 6
        },
        {
            'title': 'Die Reise zum Mond',
            'description': 'Eine spannende Reise zu den Sternen.',
            'coverImage': 'http://localhost:5000/static/images/cover2.jpg',
            'suitableRoles': ['Papa', 'Onkel'],
            'minAge': 5,
            'maxAge': 8
        },
        {
            'title': 'Die Schatzsuche im Garten',
            'description': 'Ein spannendes Abenteuer direkt vor der Haustür.',
            'coverImage': 'http://localhost:5000/static/images/cover3.jpg',
            'suitableRoles': ['Oma', 'Tante'],
            'minAge': 4,
            'maxAge': 7
        },
        # Weitere Geschichten hinzufügen...
    ]

    stories_collection.insert_many(stories)
    print('Beispieldaten eingefügt.')

if __name__ == '__main__':
    seed_data()
