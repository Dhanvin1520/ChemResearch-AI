import mongomock
from app.config import settings

class Database:
    client: mongomock.MongoClient = None
    db = None

    @classmethod
    def connect_db(cls):
        if cls.client is None:
            cls.client = mongomock.MongoClient()
            cls.db = cls.client[settings.mongodb_db_name]

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect_db()
        return cls.db

def get_db():
    return Database.get_db()
