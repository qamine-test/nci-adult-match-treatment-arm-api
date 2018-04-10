#!/bin/bash
gem install travis
pip install 'requests[security]'
pip install awscli --upgrade
export BUCKETNAME="publictoprivate"
export ENVFILENAME=`echo $TRAVIS_REPO_SLUG|sed -e 's/BIAD\///'`
travis login --github-token $GITHUB_TOKEN --org
travis env list -r $TRAVIS_REPO_SLUG|sed -e 's/=.*$//' > TRAVLIST
travis logout
env > env.txt
for var in `cat TRAVLIST|grep -v ^#`;do
    grep $var env.txt|sed -e 's/=/ /'
done >> $ENVFILENAME
aws s3 cp $ENVFILENAME s3://$BUCKETNAME --region=us-east-1
