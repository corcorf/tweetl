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

docker stop $MONGO_CONTAINER_NAME
docker rm $MONGO_CONTAINER_NAME

docker run --name $MONGO_CONTAINER_NAME -it \
-p $MONGO_PORT:27017 \
--net=$NETWORK_NAME \
-d \
mongo:4.2.5
