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
import os
import pymongo

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

        mongo_client = pymongo.MongoClient(uri)
        self.database = mongo_client[db]

    def get_documents(self, coll_name):
        return self.database[coll_name].find()

    def put_treatment_arms_documents(self, doc):
        return self.database.treatmentArms.insert_one(doc).inserted_id

    def clear_treatment_arms(self):
        self.database.treatmentArms.remove({})


class ConverterBase(object):
    """Base class for conversion objects.  Couples together the source 
       collection and the code used to convert it to the desired format
       for the new treatmentArms collection.
    """
    def __init__(self, coll_name):
        self._coll_name = coll_name

    def convert(self, doc):
        raise NotImplementedError("convert method must be implemented by child class!")

    def get_collection_name(self):
        return self._coll_name


class TAConverter(ConverterBase):
    """Converts a document from the treatment collection to a document 
       for the treatmentArms collection.
    """
    def __init__(self):
        ConverterBase.__init__(self, 'treatmentArm')

    def convert(self, ta_doc):
        if(ta_doc is None
           or '_id' not in ta_doc
           or ta_doc['_id'] is None
           or 'treatmentId' in ta_doc
           ):
            raise Exception('Invalid treatmentArm document')

        new_ta_doc = dict(ta_doc)
        del new_ta_doc['_id']
        new_ta_doc['treatmentId'] = ta_doc['_id']
        new_ta_doc['dateArchived'] = None
        return new_ta_doc


class TAHConverter(ConverterBase):
    """Converts a document from the treatmentArmHistory collection to a 
       document for the treatmentArms collection.
    """

    def __init__(self):
        ConverterBase.__init__(self, 'treatmentArmHistory')

    def convert(self, tah_doc):
        if(tah_doc is None
           or '_id' not in tah_doc
           or tah_doc['_id'] is None
           or 'treatmentArm' not in tah_doc
           or '_id' not in tah_doc['treatmentArm']
           or tah_doc['treatmentArm']['_id'] is None
           or 'dateArchived' not in tah_doc
           or tah_doc['dateArchived'] is None
           ):
            raise Exception('Invalid treatmentArmHistory document')

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


def convert_to_treatment_arms(db_accessor, converter):
    """Using the db_accessor, get all of the documents from src_collection, convert
       them to the required format using the convert_document function, and insert
       them into the treatmentArms collection.
    """
    LOGGER.info("\nConverting documents from %s into documents for treatmentArms...", converter.get_collection_name())
    cnt = 0
    for doc in db_accessor.get_documents(converter.get_collection_name()):
        new_doc = converter.convert(doc)
        new_id = db_accessor.put_treatment_arms_documents(new_doc)

        log_msg = "  TreamentArms document %s created from %s.%s"
        LOGGER.debug(log_msg, new_id, converter.get_collection_name(), doc['_id'])
        cnt += 1

    LOGGER.info("%d documents inserted into treatmentArms from %s", cnt, converter.get_collection_name())


def main():
    try:
        db_accessor = MongoDbAccessor()
        prepare_treatment_arms_collection(db_accessor)
        convert_to_treatment_arms(db_accessor, TAConverter())
        convert_to_treatment_arms(db_accessor, TAHConverter())

    except Exception as e:
        print("Unexpected error:", str(e))
        return -1

    return 0


if __name__ == '__main__':
    exit(main())
