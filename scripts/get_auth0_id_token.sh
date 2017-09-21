#!/usr/bin/env bash

# *******************************************************************
# * Script to run curl commands for retrieving id_token.                       *
# *******************************************************************

# Run the following command to set an environment variable to the token id:
# export TOKEN_ID=`get_auth0_id_token.sh 2> /dev/null | perl -ne 'print $1 if $_ =~ /"id_token":"([^"]+)"/;'`

response= curl -H "Content-Type: application/json" -X POST -d '{"client_id":"'"$AUTH0_CLIENT_ID"'","username":"'"$AUTH0_USERNAME"'","password":"'"$AUTH0_PASSWORD"'","grant_type":"password","scope":"openid roles email","connection":"'"$AUTH0_DATABASE"'"}' https://ncimatch.auth0.com/oauth/ro
