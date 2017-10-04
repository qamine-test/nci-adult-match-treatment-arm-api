from pymongo import MongoClient
import os
import sys

uri = os.environ.get('MONGODB_URI', None)
if uri is None:
    print("Required MONGODB_URI Env Var is missing.")
    sys.exit(64)

mongo_client = MongoClient(uri)
database = mongo_client['Match']
collection = database['treatmentArms']
count = collection.count({})
print("{} arms in treatmentArms".format(count))
collection.find({ 'dateArchived': None }, )
