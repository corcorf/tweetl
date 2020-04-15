# tweetl
Containerised ETL pipeline for sentiment analysis of tweets.

NB: this repo requires you to have your own API keys for Twitter and Slack. You'll also need to have docker up and running on your machine.

## Usage:
- rename or copy .env_example as .env
- add your own api credentials to the .env file as indicated by the comments
- ```source start_all.sh <keywords>```

## Features:
- Fully scripted ETL data pipeline
- Separate Docker containers for all processes
- Streaming tweets from Twitter API using tweepy
- MongoDB for immediate storage of tweets
- ETL using python, sqlalchemy, pymongo, pandas
- Sentiment analysis with Vader
- Single Docker image with pip-installable tweetl python package for tweet collection, etl and slack-bot functions

## Coming Soon...
- Container management with Kubernetes
- ETL scheduling with Airflow
