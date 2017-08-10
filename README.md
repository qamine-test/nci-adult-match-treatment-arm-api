# NCI Adult MATCH Treatment Arm API

[![Build Status](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api.svg?branch=master)](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8381ca15e9e341fdaf7036ff0a5d57e5)](https://www.codacy.com/app/FNLCR/nci-adult-match-treatment-arm-api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBIIT/nci-adult-match-treatment-arm-api&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8381ca15e9e341fdaf7036ff0a5d57e5)](https://www.codacy.com/app/FNLCR/nci-adult-match-treatment-arm-api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBIIT/nci-adult-match-treatment-arm-api&amp;utm_campaign=Badge_Coverage)

## Prerequisites

* [Install Python3.6.1](http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html)
* [Setup Virtual Environments](https://realpython.com/blog/python/python-virtual-environments-a-primer/)
* Required Python modules should be installed with the following command:
    ```bash
    pip3 install -r requirements.txt
    ```

## Development Setup

To create new venv:

```bash
mkvirtualenv nci-adult-match-treatment-arm-api
```

To switch to existing vevn:

```bash
workon nci-adult-match-treatment-arm-api
```

#### If you use VS Code

* In your terminal, activating the `nci-adult-match-treatment-arm-api` venv
* Install pylint by running pip install pylint by running `pip install pylint`
* Add shell command so be able to [start VS Code from terminal](https://code.visualstudio.com/docs/setup/mac#_command-line)
* Close all instances of VS Code
* Launch VS Code from within this terminal window (this will ensure the VS Code process will inherit all of the Virtual Env environment settings)

## To run locally

### Export environment variable for shell session

```bash
export MONGODB_URI=mongodb://localhost:27017/Match
export ENVIRONMENT='development'
export AWS_SECRET_ACCESS_KEY={your_aws_secret_access_key}
export AWS_ACCESS_KEY_ID={your_aws_access_key_id}
export PYTHONPATH=.:{your path here}/nci-adult-match-treatment-arm-api
```

### Set explicitly for a specific command execution

```bash
MONGODB_URI=mongodb://localhost:27017/Match python app.py
```

## Dockerization

*Note: you need to have access to FNLCR private docker repository. Please contact systems team if you need the access.*

To build the production image based on Apache run the following:

```bash
docker build -t "fnlcr/nci-adult-match-treatment-arm-api:latest" .
```

Starts Treatment Arm API and MongoDB:

```bash
docker-compose up
```

If you'd like to start only Monbgo DB to develop your service locally:

```bash
docker-compose up mongo
```

#### To start the container stand-alone but attached to the Docker network

Example with connecting to `nciadultmatchui_adult-match-net` Docker network. Replace with yours if needed.

```bash
docker run --name ncimatch-adult-treatment-arm-api -it --network nciadultmatchui_adult-match-net -e ENVIRONMENT=test -e MONGODB_URI=mongodb://mongo:27017/Match -p 5010:5010 fnlcr/nci-adult-match-treatment-arm-api:latest
```

## Restoring Data to Mongo DB for Local Development
These instructions apply both to dockerized MongoDB (see above for how to access this) and to a local copy
of MongoDB you may have installed.

Do the restore from from the Linux shell to dockerized Mongo (see command for this above):
```bash
mongo Match --eval "db.dropDatabase()"
mongorestore --db Match ./backup
```

Do the restore from from the Linux shell to local Mongo:
```bash
mongo Match --eval "db.dropDatabase()"
mongorestore --db Match ./data_setup/match
```

After you've restored the backup you may check the restored data

```bash
mongo shell
show dbs
use Match
show collections
db.treatmentArms.count()
```

Exit from MongoDB shell by pressing `Ctrl+C` or typing `exit`.


## Configuration
Various configuration settings can be customized in the `config/environment.yml` file.

## Misc

To find a service listening on a specific port

```bash
lsof -n -i4TCP:5010 | grep LISTEN
```

To kill a service on a specific port

```bash
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
coverage run -m unittest discover tests; coverage run -a -m unittest discover scripts/tests; coverage report -m
```

## Scripts
To run the scripts from their source directory, make sure that the path to the TreatmentArmAPI root directory is 
included in the PYTHONPATH environment variable (see section on environment variables above).

The scripts require the following:

* python 3
* pymongo 3.4 python module

Defaults to connect to the MongoDB at ```mongodb://localhost:27017/Match```; can be overwritten by setting the 
MONGODB_URI environment variable to the desired URI.

#### consolidate_treatment_arms
Merge the treatmentArm and treatmentArm collections in MongoDB Match database into single treatmentArms collection.

```bash
python3 scripts/consolidate_treatment_arm_collections/consolidate_treatment_arm_collections.py
```

#### refresh_summary_report.py
Refreshes the summaryReport field of the active arms in the treatmentArms collection.  Ordinarily this process will be 
started via message to the TreatmentArmQueue in SQS.  Running the script manually as shown below is provided primarily 
to make development and testing easier.

```bash
python3 scripts/summary_report_refresher/refresh_summary_report.py
```

#### ta_message_manager.py
Creates and monitors the TreatmentArmQueue in SQS.
```bash
python3 scripts/ta_message_manager/ta_message_manager.py
```
Currently only responds to two messages:
* "RefreshSummaryReport":  runs the summary report refresh process.
* "STOP":  shuts down the ta_message_manager.

To easily send either of these messages to the message manager from the command line:
```bash
python3 -c "import scripts.ta_message_manager.ta_message_manager as tmm; tmm.send_message_to_ta_queue(tmm.REFRESH_MSG)"
python3 -c "import scripts.ta_message_manager.ta_message_manager as tmm; tmm.send_message_to_ta_queue(tmm.STOP_MSG)"
```

## Helpful Aliases
Add these to your .bashrc:

For building docker image:
```bash
alias tabuild='docker build -t "fnlcr/nci-adult-match-treatment-arm-api:latest" .'
```
For running all tests with coverage:
```bash
alias tacov='cd {path to treatmentArmApi source}; coverage run -m unittest discover tests; coverage run -a -m unittest discover scripts/tests; coverage report -m; cd -'
```
