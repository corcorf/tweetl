"""
Module containing the extract-transform-load job for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import os
from time import time

from dotenv import load_dotenv

from mongo_operations import extract_tweets, transform_data
from sql_operations import CONN_STRING
from sql_operations import write_to_tweet_database
from tweetl_log import set_up_log

load_dotenv()

if __name__ == "__main__":
    HOST = "tweet_collector_mongodb_1"
    FREQ = 300
    LOG = set_up_log(level=os.getenv("LOGGING_LEVEL"))
    LAST_PULL = 0
    LOG.debug('Initialising pull time: %s', LAST_PULL)

    while True:
        extracted, LAST_PULL = extract_tweets(LAST_PULL, HOST)
        transformed = transform_data(extracted)
        write_to_tweet_database(transformed, CONN_STRING)
        LOG.debug('etl_round_done')
        time.sleep(FREQ)
