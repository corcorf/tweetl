#!/bin/bash

keyword=$1
container_name="${TWEET_COLLECTOR_IMAGE_NAME}_${keyword}"

docker stop $container_name
docker rm $container_name

docker run --name $container_name -it \
-e KEYWORDS=$keyword \
--net=$NETWORK_NAME \
-d $TWEET_COLLECTOR_IMAGE_NAME:latest
