#!/bin/bash

echo
echo "#######################"
echo "Running script $0"
if [ $# -ne 0 ]
then
  echo "Arguments: $@"
fi
echo "#######################"
echo

keyword=$1
echo "container keyword $keyword"
container_name=$AIRFLOW_JOB_CONTAINER_NAME
host_log_dir=logs
echo "host_log_dir: ${PWD}/${host_log_dir}"

docker stop $container_name
docker rm $container_name

if ! [ -d $host_log_dir ]
then
  mkdir $host_log_dir
fi

docker run --name $container_name -it \
-e CONTAINER_NAME=${container_name} \
-e KEY_WORDS=$keyword \
--net=$NETWORK_NAME \
-v ${PWD}/${host_log_dir}:$CONTAINER_LOG_PATH \
--link $PG_CONTAINER_NAME \
--link $MONGO_CONTAINER_NAME \
--user "airflow" \
--entrypoint "/entrypoint.sh" \
-p 8080:8080 \
-d \
tweetl:latest \
"webserver"
