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

container_name=$ETL_JOB_CONTAINER_NAME
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
--net=$NETWORK_NAME \
-v ${PWD}/${host_log_dir}:$CONTAINER_LOG_PATH \
--link $PG_CONTAINER_NAME \
--link $MONGO_CONTAINER_NAME \
-d \
tweetl:latest \
etl \
--mongo_hostname $MONGO_CONTAINER_NAME \
--freq $ETL_FREQUENCY \
--pg_hostname $PG_CONTAINER_NAME \
--pg_database $PG_DB_NAME \
--pg_port 5432 \
--pg_user $PG_USER \
--pg_password $PG_PASSWORD
