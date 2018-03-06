#! /bin/bash

NEW_RELIC_ENVIRONMENT=${ENVIRONMENT} NEW_RELIC_CONFIG_FILE=/usr/app/custom-newrelic.ini newrelic-admin run-program python ./app.py
