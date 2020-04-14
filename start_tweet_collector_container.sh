#!/bin/bash

keyword=$1
echo "container keyword $keyword"
container_name="${TWEET_COLLECTOR_IMAGE_NAME}_${keyword}"
host_log_dir=logs
echo "host_log_dir: ${PWD}/${host_log_dir}"

docker stop $container_name
docker rm $container_name

if ! [ -d $host_log_dir ]
then
  mkdir $host_log_dir
fi

docker run --name $container_name -it \
-e KEYWORDS=$keyword \
-e CONTAINER_NAME=${container_name} \
--net=$NETWORK_NAME \
-v ${PWD}/${host_log_dir}:$CONTAINER_LOG_PATH \
--link $MONGO_CONTAINER_NAME \
$TWEET_COLLECTOR_IMAGE_NAME:latest
