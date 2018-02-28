#!/usr/bin/env python3
"""
Consolidate collections treatmentArm and treatmentArmHistory into a single
treatmentArms collection.

The new treatmentArms collection will look much like the old treatmentArm collection
with the following changes/additions:
*  treatmentArm._id currently contains the unique identifier for each
   treatment arm; because it functions as a primary key, it needs to be
   renamed treatmentArmId.
   - For documents from treatmentArmHistory, treatmentArmId will originate from _id of
     the treatmentArm subcollection.
*  mongoDB will auto-generate a new unique _id
*  add 'dateArchived' key; the active arm will be identified by dateArchived IS NULL and archived
   arms will get this value from treatmentArmHistory.
*  add 'studyTypes' list; will contain or both of these:  'STANDARD', 'OUTSIDE_ASSAY'
*  add 'stateToken' key with UUID.
*  '_class' will be 'gov.match.model.TreatmentArm' for all documents.
*  remove 'exclusionCriterias' because it is obsolete and will be excluded from treatmentArms
*  for active arms only (that is, documents with dateArchived == null), add 'summaryReport' key, which
   will contain a subcollection with the following items with default values:
        - 'numCurrentPatientsOnArm': 0,
        - 'numFormerPatients': 0,
        - 'numPendingArmApproval': 0,
        - 'numNotEnrolledPatient': 0,
        - 'assignmentRecords': []

Note:  In production, this script will need to be run only once.  To simplify
development/testing efforts, it will first remove all documents from the
treatmentArms collection if they exist.

Returns 0 if successful; otherwise -1.
"""
import logging
import os
import sys
import uuid

from config import log
from scripts.consolidate_treatment_arm_collections.consolidate_ta_mongo_db_accessor import MongoDbAccessor

# Logging functionality
log.log_config()
LOGGER = logging.getLogger(__name__)

OA_ARMS = ['EAY131-A', 'EAY131-C1', 'EAY131-C2', 'EAY131-E', 'EAY131-F', 'EAY131-G', 'EAY131-H', 'EAY131-L',
           'EAY131-M', 'EAY131-R', 'EAY131-S2', 'EAY131-T', 'EAY131-U', 'EAY131-V', 'EAY131-X', 'EAY131-Y',
           'EAY131-Z1B', 'EAY131-Z1C', 'EAY131-Z1E']

def get_study_types(treatmentArmId):
    if treatmentArmId not in OA_ARMS:
        return ['STANDARD']
    else:
        return ['STANDARD', 'OUTSIDE_ASSAY']


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

    @staticmethod
    def _apply_common_changes(new_ta_doc):
        new_ta_doc['studyTypes'] = get_study_types(new_ta_doc['_id'])
        del new_ta_doc['_id']
        if 'exclusionCriterias' in new_ta_doc:
            del new_ta_doc['exclusionCriterias']
        new_ta_doc['_class'] = 'gov.match.model.TreatmentArm'
        new_ta_doc['stateToken'] = str(uuid.uuid4())


class TAConverter(ConverterBase):
    """Converts a document from the treatment collection to a document
       for the treatmentArms collection.
    """
    EMPTY_SUMMARY_REPORT = {'numCurrentPatientsOnArm': 0,
                            'numFormerPatients': 0,
                            'numPendingArmApproval': 0,
                            'numNotEnrolledPatient': 0,
                            'assignmentRecords': []}

    def __init__(self):
        ConverterBase.__init__(self, 'treatmentArm')

    def convert(self, doc):
        if(doc is None
           or '_id' not in doc
           or doc['_id'] is None
           or 'treatmentArmId' in doc
           ):
            raise Exception('Invalid treatmentArm document')

        new_ta_doc = dict(doc)
        ConverterBase._apply_common_changes(new_ta_doc)
        new_ta_doc['treatmentArmId'] = doc['_id']
        new_ta_doc['dateArchived'] = None
        new_ta_doc['summaryReport'] = TAConverter.EMPTY_SUMMARY_REPORT
        return new_ta_doc


class TAHConverter(ConverterBase):
    """Converts a document from the treatmentArmHistory collection to a
       document for the treatmentArms collection.
    """

    def __init__(self):
        ConverterBase.__init__(self, 'treatmentArmHistory')

    def convert(self, doc):
        if(doc is None
           or '_id' not in doc
           or doc['_id'] is None
           or 'treatmentArm' not in doc
           or '_id' not in doc['treatmentArm']
           or doc['treatmentArm']['_id'] is None
           or 'dateArchived' not in doc
           or doc['dateArchived'] is None
           ):
            raise Exception('Invalid treatmentArmHistory document')

        new_ta_doc = dict(doc['treatmentArm'])
        ConverterBase._apply_common_changes(new_ta_doc)
        new_ta_doc['treatmentArmId'] = doc['treatmentArm']['_id']
        new_ta_doc['dateArchived'] = doc['dateArchived']
        return new_ta_doc


def prepare_treatment_arms_collection(db_accessor):
    """It is necessary to remove any existing documents from treatmentArms prior
       to adding the items from the other source tables.
    """
    trtmt_arms_cnt = db_accessor.get_document_count('treatmentArms')
    if trtmt_arms_cnt:
        LOGGER.info('treatmentArms must be empty; %d documents will be removed before continuing.',
                    trtmt_arms_cnt)

        db_accessor.clear_treatment_arms()
        trtmt_arms_cnt = db_accessor.get_document_count('treatmentArms')

        LOGGER.info("treatmentArms now contains %d documents", trtmt_arms_cnt)

    return trtmt_arms_cnt  # should always return 0; used for unit-testing


def convert_to_treatment_arms(db_accessor, converter):
    """Using the db_accessor, get all of the documents from collection named in converter,
       convert them to the required format using the converter.convert function, and insert
       them into the treatmentArms collection.
       Return the number of documents converted.
    """
    LOGGER.info("\nConverting documents from %s into documents for treatmentArms...",
                converter.get_collection_name())

    cnt = 0
    for doc in db_accessor.get_documents(converter.get_collection_name()):
        new_doc = converter.convert(doc)
        new_id = db_accessor.put_treatment_arms_documents(new_doc)
        cnt += 1

        log_msg = "  TreamentArms document %s created from %s.%s"
        LOGGER.debug(log_msg, new_id, converter.get_collection_name(), doc['_id'])

    LOGGER.info("%d documents inserted into treatmentArms from %s", cnt, converter.get_collection_name())
    return cnt


def main(db_accessor):
    try:
        prepare_treatment_arms_collection(db_accessor)
        doc_cnt = convert_to_treatment_arms(db_accessor, TAConverter())
        doc_cnt += convert_to_treatment_arms(db_accessor, TAHConverter())

        LOGGER.info("\n%d total documents inserted into treatmentArms.", doc_cnt)

    except Exception as e:
        LOGGER.exception("Unexpected error:" + str(e))
        return -1

    return 0


LOCAL_DB_DEBUG_LOG_MSG = "Connecting to local MongoDB"
ENV_VAR_DEBUG_LOG_MSG = "Connecting to MongoDB specified in MONGODB_URI"
DEFAULT_URI = 'mongodb://localhost:27017/Match'

def get_mongo_accessor():
    if 'MONGODB_URI' in os.environ:
        LOGGER.debug(ENV_VAR_DEBUG_LOG_MSG)
        uri = os.environ['MONGODB_URI']
    else:
        LOGGER.debug(LOCAL_DB_DEBUG_LOG_MSG)
        uri = DEFAULT_URI

    # Some instances of the DB are named 'Match' and others 'match'.
    db = 'match' if '/match' in uri else 'Match'
    return MongoDbAccessor(uri, db)


if __name__ == '__main__':
    if sys.version_info >= (3, 6, 0):
        LOGGER.warning("Script may not run with python 3.6; please try python 3.5 if you have problems.\n")

    exit(main(get_mongo_accessor()))
