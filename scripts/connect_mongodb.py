import os
import ssl
import sys
import traceback

from pymongo import MongoClient

uri = os.environ.get('MONGODB_URI', None)
if uri is None:
    print("Required MONGODB_URI Env Var is missing.")
    sys.exit(64)

try:
    mongo_client = MongoClient(uri)
    # mongo_client = MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)
except Exception as e:
    print("Exception caught during connection.")
    print(str(e))
    sys.exit(128)

try:
    database = mongo_client['Match']
except Exception as e:
    print(traceback.format_exc())
    print("Exception caught getting Match database.")
    print(str(e))
    sys.exit(128)

try:
    collection = database['treatmentArms']
except Exception as e:
    print(traceback.format_exc())
    print("Exception caught getting treatmentArms collection.")
    print(str(e))
    sys.exit(128)

try:
    count = collection.count({})
except Exception as e:
    print(traceback.format_exc())
    print("Exception caught getting treatmentArms count.")
    print(str(e))
    sys.exit(128)
else:
    print("{} arms in treatmentArms".format(count))

try:
    count = database['treatmentArm'].count({})
except Exception as e:
    print("Exception caught getting treatmentArm count.")
    print(str(e))
    sys.exit(128)
else:
    print("{} arms in treatmentArm".format(count))

try:
    count = database['treatmentArmHistory'].count({})
except Exception as e:
    print("Exception caught getting treatmentArmHistory count.")
    print(str(e))
    sys.exit(128)
else:
    print("{} arms in treatmentArmHistory".format(count))
