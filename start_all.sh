#!/bin/bash

# check arguments have been passed
if [ $# -eq 0 ]
then
  echo
  echo $0: usage: start_all keywords
  echo
else
  # read in keywords to collect tweets for
  keywords=$@
  echo
  echo "#######################"
  echo "Keywords are $keywords"
  echo "#######################"
  echo
  # get environment variables from .env
  echo
  echo "#######################"
  echo "Getting environment variables from .env"
  echo "#######################"
  echo
  source .env

  # start docker daemon
  echo
  echo "#######################"
  echo "Starting Docker daemon"
  echo "#######################"
  echo
  systemctl --user start docker

  # create network over which docker containers can communicate
  # docker network ls --filter name="tweet_network" -q
  echo
  echo "#######################"
  echo "Creating Docker bridge network"
  echo "#######################"
  echo
  docker network create --driver bridge tweet_network

  ## build and run all containers

  /bin/bash start_mongo_container.sh
  /bin/bash start_postgres_container.sh
  # sleep long enough to allow mongo to initialise
  /bin/bash build_tweetl_image.sh
  for kw in $keywords
  do
    /bin/bash start_tweet_collector_container.sh $kw
  done
  /bin/bash start_airflow_container.sh $kw
  # /bin/bash start_etl_job_container.sh
  # /bin/bash start_slack_bot_container.sh $kw
  echo
  echo Done
fi
echo
