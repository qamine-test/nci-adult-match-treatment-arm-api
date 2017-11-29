#!/usr/bin/env bash

# *******************************************************************
# * Script to run curl commands for retrieving id_token.                       *
# *******************************************************************

echo "Creating token for user $AUTH0_USERNAME on $AUTH0_DATABASE"
response= curl -H "Content-Type: application/json" -X POST -d '{"client_id":"'"$AUTH0_CLIENT_ID"'","username":"'"$AUTH0_USERNAME"'","password":"'"$AUTH0_PASSWORD"'","grant_type":"password","scope":"openid roles email","connection":"'"$AUTH0_DATABASE"'"}' https://ncimatch.auth0.com/oauth/ro

# Run the following command to set an environment variable to the token id:
# export TOKEN_ID=`get_auth0_id_token.sh 2> /dev/null | perl -ne 'print $1 if $_ =~ /"id_token":"([^"]+)"/;'`

# Once the token is established, it can be used to access the API with curl.  For example:
# curl -v "https://match-int.nci.nih.gov/api/v1/treatment_arms/dashboard/overview" --header "authorization: Bearer ${TOKEN_ID}"

# Suggested addition to your .bashrc:
# function newtoken {  # Sets the TOKEN_ID env var to an Auth0 authentication token.
#     export TOKEN_ID=`{PATH_TO_nci-adult-match-treatment-arm-api}/scripts/get_auth0_id_token.sh 2> /dev/null | perl -ne 'print $1 if $_ =~ /"id_token":"([^"]+)"/;'`
# }
# Once this function is added to your .bashrc, you will only need to execute "newtoken" on the command line to
# generate a new token and assign it to the environment variable.
