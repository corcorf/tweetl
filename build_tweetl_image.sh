#! /bin/bash

echo
echo "#######################"
echo "Running script $0"
if [ $# -ne 0 ]
then
  echo "Arguments: $@"
fi
echo "#######################"
echo

build_context_dir=build_context_tweetl
if ! [ -d $build_context_dir ]
then
  mkdir $build_context_dir
fi
docker_filename="$build_context_dir/Dockerfile"
cp Dockerfile $docker_filename
cp -r tweetl $build_context_dir
cp setup.py $build_context_dir
cp requirements.txt $build_context_dir
cp .env $build_context_dir
docker build -f $docker_filename -t tweetl:latest $build_context_dir

rm -r $build_context_dir
