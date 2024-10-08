# utils/database.py

from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]
