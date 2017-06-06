# NCI Adult MATCH Treatment Arm API

[![Build Status](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api.svg?branch=master)](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8381ca15e9e341fdaf7036ff0a5d57e5)](https://www.codacy.com/app/FNLCR/nci-adult-match-treatment-arm-api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBIIT/nci-adult-match-treatment-arm-api&amp;utm_campaign=Badge_Grade)

## Prerequisites

* [Install Python3.5](http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html)
* [Setup Virtual Environments](https://realpython.com/blog/python/python-virtual-environments-a-primer/)
* Required Python modules:  pymongo, flask, flask_env, flask_cors, flask_restful

## Development Setup

To create new venv:

```#!/bin/bash
mkproject nci-adult-match-treatment-arm-api
```

To switch to existing vevn:

```#!/bin/bash
workon nci-adult-match-treatment-arm-api
```

### If you use VS Code

* In your terminal, activating the `nci-adult-match-treatment-arm-api` venv
* Install pylint by running pip install pylint by running `pip install pylint`
* Add shell command so be able to [start VS Code from terminal](https://code.visualstudio.com/docs/setup/mac#_command-line)
* Close all instances of VS Code
* Launch VS Code from within this terminal window (this will ensure the VS Code process will inherit all of the Virtual Env environment settings)

## To run locally

### Export environment variable for shell session

```#!/bin/bash
export MONGODB_URI=mongodb://localhost:27017/match
```

### Set explicitly for a specific command execution

```#!/bin/bash
MONGODB_URI=mongodb://localhost:27017/match python app.py
```

## Dockerization

*Note: you need to have access to FNLCR private docker repository. Please contact systems team if you need the access.*

To build the production image based on Apache run the following:

```#!/bin/bash
docker build -t "fnlcr/nci-adult-match-treatment-arm-api:latest" .
```

Starts Treatment Arm API and MongoDB:

```#!/bin/bash
docker-compose up
```

If you'd like to start only Monbgo DB to develop your service locally:

```#!/bin/bash
docker-compose up mongo
```

To restore MongoDB data for your local development:

```#!/bin/bash
docker exec -it nciadultmatchtreatmentarmapi_mongo_1 bash
mongorestore --db Match ./backup
```

After you've restored the backup you may check the restored data (while still attached to the mongo container, as above):

```#!/bin/bash
mongo shell
show dbs
use match
show collections
db.treatmentArm.count()
```

Exit from MongoDB shell by pressing `Ctrl+C`

### To start the container stand-alone but attached to the Docker network

Example with connecting to `nciadultmatchui_adult-match-net` Docker network. Replace with yours if needed.

```#!/bin/bash
docker run --name ncimatch-adult-treatment-arm-api -it --network nciadultmatchui_adult-match-net -e ENVIRONMENT=test -e MONGODB_URI=mongodb://mongo:27017/Match -p 5010:5010 fnlcr/nci-adult-match-treatment-arm-api:latest
```

## Misc

To find a service listening on a specific port

```#!/bin/bash
lsof -n -i4TCP:5010 | grep LISTEN
```

To kill a service on a specific port

```#!/bin/bash
kill -9 $(lsof -n -i4TCP:5010)
```
## Unit Tests
To run the unit tests, make sure that the path to the TreatmentArmAPI root directory is included in the PYTHONPATH
environment variable.

To run a single unit test:
```
python3 <testfile>.py
```

To run all unit tests:
```
python3 -m unittest discover <test_directory>
```

To run all tests with the coverage tool, execute the following from the TreatmentArmAPI root directory:
```
coverage run -m unittest discover tests; coverage report -m
```

## Scripts

####consolidate_treatment_arms
Merge the treatmentArm and treatmentArm collections in MongoDB Match database into single treatmentArms collection.

 
* python 3 (must be 3.5 or earlier)
* pymongo 3.4 python module

Defaults to connect to the MongoDB at ```mongodb://localhost:27017/match```; can be overwritten by setting the MONGODB_URI 
environment variable to the desired URI.

```#!/bin/bash
python3 scripts/consolidate_treatment_arm_collections/consolidate_treatment_arm_collections.py
```
