from pymongo import MongoClient


class NoResultsFound(Exception):
    pass


class MongoDBGateway:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def get(self, query: dict) -> list:
        result = list(self._collection.find(query))
        if not result:
            raise NoResultsFound("Documents are not found for the specified criteria.")
        return result
