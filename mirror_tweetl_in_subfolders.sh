#!/bin/bash

# create hard links to tweetl in all sub-folders
module_name="tweetl"
source_dir="$PWD/$module_name/"
env_dir="$PWD/env/"
echo "Creating hard links to the contents of $module_name module in\
 subdirectory:"
for dst_dir_name in $@
do
  dst_dir_path="$PWD/${dst_dir_name}/"
  if [ $dst_dir_path != $source_dir ] && [ $dst_dir_path != $env_dir ]
  then
    echo -e ' \t '$dst_dir_name
    if ! [ -d $dst_dir_path ]
    then
      mkdir $dst_dir_path
    fi
    mirror_dir=$dst_dir_path$module_name
    if ! [ -d $mirror_dir ]
    then
      mkdir $mirror_dir
    fi
    for pyfile in ${source_dir}*.py
    do
      cp $pyfile $mirror_dir
    done
  fi
done
