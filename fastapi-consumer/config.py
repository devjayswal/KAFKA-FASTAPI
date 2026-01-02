from pymongo import MongoClient
from models.Message import MessageSettings

settings = MessageSettings()
client = MongoClient(settings.mongo_connection_string)
db = client[settings.mongo_database_name]
collection = db[settings.mongo_collection_name]

try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Connected to the database successfully")
except Exception as e:
    print(f"Error connecting to the database: {e}")

