"""
Consolidate collections treatmentArm and treatmentArmHistory into a single 
treatmentArms collection.
Notes:
*  treatmentArm._id currently contains the unique identifier for each 
   treatment arm; because it functions as a primary key, it needs to be 
   renamed treatmentId
*  mongoDB will auto generate a new unique _id
*  active arm will be identified by dateArchived IS NULL
"""
import logging
import sys
import os
from pymongo import MongoClient

# Logging functionality
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())


class MongoDbAccessor(object):

    def __init__(self):

        host = os.environ.get('MONGO_HOST', 'localhost')
        port = os.environ.get('MONGO_PORT', 27017)
        db = 'Match'
        uri = f"mongodb://{host}:{port}/{db}"

        mongo_client = MongoClient(uri)
        self.database = mongo_client[db]

    def get_treatment_arm_documents(self):
        return self.database.treatmentArm.find()

    def get_treatment_arm_history_documents(self):
        return self.database.treatmentArmHistory.find()

    def get_documents(self, coll_name):
        return self.database[coll_name].find()

    def put_treatment_arms_documents(self, doc):
        return self.database.treatmentArms.insert_one(doc).inserted_id

    def clear_treatment_arms(self):
        self.database.treatmentArms.remove({})


def ta_to_new_ta(ta_doc):
    """Converts a document from the treatment collection to a document 
       for the treatmentArms collection.
    """
    new_ta_doc = dict(ta_doc)
    del new_ta_doc['_id']
    new_ta_doc['treatmentId'] = ta_doc['_id']
    new_ta_doc['dateArchived'] = None
    return new_ta_doc


def tah_to_new_ta(tah_doc):
    """Converts a document from the treatmentArmHistory collection to a 
       document for the treatmentArms collection.
    """
    new_ta_doc = dict(tah_doc['treatmentArm'])
    del new_ta_doc['_id']
    new_ta_doc['_class'] = 'gov.match.model.TreatmentArm'
    new_ta_doc['treatmentId'] = tah_doc['treatmentArm']['_id']
    new_ta_doc['dateArchived'] = tah_doc['dateArchived']
    return new_ta_doc


def prepare_treatment_arms_collection(db_accessor):
    """It is necessary to remove any existing documents from treatmentArms prior
       to adding the items from the other source tables.
    """
    trtmt_arms_cnt = db_accessor.get_documents('treatmentArms').count()
    if trtmt_arms_cnt:
        LOGGER.info('treatmentArms must be empty!; %d documents will be removed before continuing.',
                    trtmt_arms_cnt)
        db_accessor.clear_treatment_arms()
        trtmt_arms_cnt = db_accessor.get_documents('treatmentArms').count()
        LOGGER.info("treatmentArms now contains %d documents", trtmt_arms_cnt)


def convert_to_treatment_arms(db_accessor, src_collection, convert_document):
    """Using the db_accessor, get all of the documents from src_collection, convert
       them to the required format using the convert_document function, and insert
       them into the treatmentArms collection.
    """
    LOGGER.info("Converting documents from %s into documents for treatmentArms", src_collection)
    for doc in db_accessor.get_documents(src_collection):
        new_doc = convert_document(doc)
        new_id = db_accessor.put_treatment_arms_documents(new_doc)
        log_msg = "TreamentArms document %s created from %s.%s"
        LOGGER.debug(log_msg, new_id, src_collection, doc['_id'])


def main():
    try:
        db_accessor = MongoDbAccessor()
        prepare_treatment_arms_collection(db_accessor)
        convert_to_treatment_arms(db_accessor, 'treatmentArm',        ta_to_new_ta)
        convert_to_treatment_arms(db_accessor, 'treatmentArmHistory', tah_to_new_ta)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return -1

    return 0


if __name__ == '__main__':
    exit(main())
