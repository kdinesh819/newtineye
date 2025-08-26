from pymongo import MongoClient

class MongoDB:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_document(self, document):
        result = self.collection.insert_one(document)
        return result.inserted_id

    def find_documents(self, query=None):
        if query is None:
            query = {}
        documents = self.collection.find(query)
        return list(documents)

    def update_document(self, query, update_values):
        update_query = {"$set": update_values}
        result = self.collection.update_one(query, update_query)
        return result.modified_count