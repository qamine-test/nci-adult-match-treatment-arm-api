import pymongo


class MongoDbAccessor(object):

    def __init__(self, uri, db):
        mongo_client = pymongo.MongoClient(uri)
        self.database = mongo_client[db]

    def get_documents(self, coll_name):
        return self.database[coll_name].find()

    def get_document_count(self, coll_name):
        return self.database[coll_name].find().count()

    def put_treatment_arms_documents(self, doc):
        return self.database.treatmentArms.insert_one(doc).inserted_id

    def clear_treatment_arms(self):
        self.database.treatmentArms.remove({})