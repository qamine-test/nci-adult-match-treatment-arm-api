# NCI Adult MATCH Treatment Arm API

[![Build Status](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api.svg?branch=master)](https://travis-ci.org/CBIIT/nci-adult-match-treatment-arm-api)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8381ca15e9e341fdaf7036ff0a5d57e5)](https://www.codacy.com/app/FNLCR/nci-adult-match-treatment-arm-api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBIIT/nci-adult-match-treatment-arm-api&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8381ca15e9e341fdaf7036ff0a5d57e5)](https://www.codacy.com/app/FNLCR/nci-adult-match-treatment-arm-api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBIIT/nci-adult-match-treatment-arm-api&amp;utm_campaign=Badge_Coverage)

## Prerequisites

* [Install Python3.6.1](http://www.marinamele.com/2014/07/install-python3-on-mac-os-x-and-use-virtualenv-and-virtualenvwrapper.html)
* [Setup Virtual Environments](https://realpython.com/blog/python/python-virtual-environments-a-primer/) 
(Explanation about virtual environments.)
    
    Install **virtualenvwrapper**:
    ```bash
    pip3 install virtualenv
    pip3 install virtualenvwrapper
    ```
    
    If you run into an error related to the package six (dependency) use:
    ```bash
    pip3 install virtualenvwrapper --ignore-installed six
    ```
    
    In your home directory, create a folder to contain your virtual environments:
    ```bash
    mkdir ~/.virtualenvs
    ```
    
    Open your **.bashrc** and add the following:
    ```bash
    export VIRTUALENVWRAPPER_PYTHON=[path to python3]
    export WORKON_HOME=~/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    ```
    
    Activate those changes with the following command:
    ```bash
    . .bashrc
    ```

## Development Setup

To create a new virtual environment named "nci-adult-match-treatment-arm-api":
```bash
mkvirtualenv --python=[python3.6_path] nci-adult-match-treatment-arm-api
```

To switch to existing existing virtual environment:
```bash
workon nci-adult-match-treatment-arm-api
```

Required Python modules should be installed in the virtual environment with the following command:
```bash
pip3 install -r requirements.txt
```

To exit the virtual environment:
```bash
deactivate 
```

Also, see section below on customizing the TreatmentArm API virtual environment.

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
export AUTH0_DATABASE={database_name}
export AUTH0_CLIENT_ID={client_id}
export AUTH0_CLIENT_SECRET={client_secret}
export AUTH0_USERNAME={uour_auth0_username}
export AUTH0_PASSWORD={uour_auth0_password}
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

Do the restore from from the Linux shell to dockerized Mongo:
```bash
docker exec -it nciadultmatchtreatmentarmapi_mongo_1 bash
mongo Match --eval "db.dropDatabase()"
mongorestore --db Match ./backup
```

Do the restore from from the Linux shell to local Mongo:
```bash
mongo Match --eval "db.dropDatabase()"
mongorestore --db Match ./data_setup/match
```

After you've restored the backup you may check the restored data:
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
UNITTEST=1 python3 <testfile>.py
```

To run all unit tests:
```
UNITTEST=1 python3 -m unittest discover <test_directory>
```

To run all tests with the coverage tool, execute the following from the TreatmentArmAPI root directory:
```
UNITTEST=1 coverage run -m unittest discover tests; UNITTEST=1 coverage run -a -m unittest discover scripts/tests; coverage report -m
```

## Scripts
To run the scripts from their source directory, make sure that the path to the TreatmentArmAPI root directory is 
included in the PYTHONPATH environment variable (see section on environment variables above OR section on 
Customizing the TreatmentArm API Virtual Environment below).

Defaults to connect to the MongoDB at ```mongodb://localhost:27017/Match```; can be overwritten by setting the 
MONGODB_URI environment variable to the desired URI.

#### consolidate_treatment_arms
Merge the treatmentArm and treatmentArm collections in MongoDB Match database into single treatmentArms collection.

```bash
python3 scripts/consolidate_treatment_arm_collections/consolidate_treatment_arm_collections.py
```

#### refresh_summary_report
Refreshes the summaryReport field of the active arms in the treatmentArms collection.  Ordinarily this process will be 
started via message to the TreatmentArmQueue in SQS.  Running the script manually as shown below is provided primarily 
to make development and testing easier.

```bash
python3 scripts/summary_report_refresher/refresh_summary_report.py
```

#### ta_message_manager
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

## Database Conversion
There are a handful of changes to the Adult Match production database that are required:

1.  Run the **consolidate_treatment_arms** script.  (See instructions above.)
2.  Run the **refresh_summary_report** script.  (See instructions above.)
3.  In the **PatientAPI** project, create indexes on the **Patient** collection.  
4.  In the **PatientAPI** project, create the Patient UI Views on the **Patient** collection. 
5.  In the **PatientAPI** project, run the script to update the field name for the Treatment Arm ID.


## Customizing the TreatmentArm API Virtual Environment
Create custom environment variables and aliases to simplify development within the virtual environment.

Recommended additions to the **postactivate** file:
```bash
export PROJECT_PATH=[path to nci-adult-match-treatment-arm-api]
export OLD_PYTHONPATH="$PYTHONPATH"
export PYTHONPATH=.:$PROJECT_PATH
VIRTUAL_ENV_NAME=`basename $VIRTUAL_ENV`
export PROMPT_COMMAND='echo -ne "\033]0;${PWD/#$PROJECT_PATH/$VIRTUAL_ENV_NAME:}\007"'
alias home='cd $PROJECT_PATH'
home

alias dbm='docker exec -it nciadultmatchtreatmentarmapi_mongo_1 bash'   # create a bash shell for accessing the dockerized MongoDB; dbm=DockerMongoBash
alias build='cd $PROJECT_PATH; docker build -t "fnlcr/nci-adult-match-treatment-arm-api:latest" .'  # builds the docker image
alias up='docker-compose up' # starts the service in docker
# For running all tests with coverage:
alias cov='cd $PROJECT_PATH; UNITTEST=1 coverage run -m unittest discover tests; UNITTEST=1 coverage run -a -m unittest discover scripts/tests; coverage report -m; cd -'
```
Recommended additions to the **postdeactivate** file:
```bash
export PYTHONPATH="$OLD_PYTHONPATH"
export PROMPT_COMMAND='echo -ne "\033]0;${PWD/#$HOME/~}\007"'
```

To find those files, use the following command while within the virtual environment:
```bash
cdvirtualenv bin
```
