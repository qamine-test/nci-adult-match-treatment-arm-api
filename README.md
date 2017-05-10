# nci-adult-match-treatment-arm-api

NCI Adult MATCH Treatment Arm API

## Prerequisites

* [Install Python3](http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html)
* [Setup Vurtial Environments](https://realpython.com/blog/python/python-virtual-environments-a-primer/)

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
export MONGO_HOST=localhost
export MONGO_PORT=27017
```

### Set explicitly for a specific command execution

```#!/bin/bash
MONGO_HOST=localhost MONGO_PORT=27017 python app.py
```

## Dockerization

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
mongorestore --db match ./backup
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

## Misc

To find a service listening on a specific port

```#!/bin/bash
lsof -n -i4TCP:5000 | grep LISTEN
```

To kill a service on a specific port

```#!/bin/bash
kill -9 $(lsof -n -i4TCP:5000)
```

## Scripts

To merge the treatmentArm and treatmentArm collections in MongoDB Match database into single treatmentArms collection:

```#!/bin/bash
python3 scripts/consolidateTAcollections/cons_ta_colls.py
```
