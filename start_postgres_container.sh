#!/bin/bash

# make directory for database data if it does not exist
if ! [ -d $PG_DB_PATH_ON_HOST ]
then
  mkdir $PG_DB_PATH_ON_HOST
fi

docker stop $PG_CONTAINER_NAME
docker rm $PG_CONTAINER_NAME

docker run --name $PG_CONTAINER_NAME -it \
-e POSTGRES_USER=$PG_USER \
-e POSTGRES_PASSWORD=$PG_PASSWORD \
-e POSTGRES_DB=$PG_DB_NAME \
-v $PG_DB_PATH_ON_HOST:/var/lib/postgresql/data \
-p $PG_PORT:5432 \
--net=$NETWORK_NAME \
-d postgres:9.6
