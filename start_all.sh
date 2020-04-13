#!/bin/bash

# read in keywords to collect tweets for
keywords=$@

# get environment variables from .env
source .env

# start docker daemon
systemctl --user start docker

# create network over which docker containers can communicate
# docker network ls --filter name="tweet_network" -q
docker network create --driver bridge tweet_network

## build and run all containers
# postgres
source start_mongo_container.sh
source start_postgres_container.sh
# sleep long enough to allow mongo to initialise

source build_tweet_collector_container.sh
for kw in keywords
do
  source start_tweet_collector_container.sh $kw
done
# source start_etl_containter.sh
# source start_slackbot_container.sh
