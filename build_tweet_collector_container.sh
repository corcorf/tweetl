#! /bin/bash

build_context_dir=$TWEET_COLLECTOR_IMAGE_NAME
source mirror_tweetl_in_subfolders.sh $build_context_dir
docker_filename="$build_context_dir/Dockerfile"
cp Dockerfile_tweet_collector $docker_filename
cp requirements.txt $build_context_dir
cp .env $build_context_dir
docker build -f $docker_filename -t $TWEET_COLLECTOR_IMAGE_NAME:latest $build_context_dir
