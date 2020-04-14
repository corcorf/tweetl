"""
Module containing all pymongo-based operations for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import logging
from time import time

import pymongo
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()
LOG = logging.getLogger('tweetl.mongo_operations')


def get_tweet_collection(hostname="mongodb", db_name="tweet_db",
                         collection_name="tweets"):
    """
    return a pymongo collection object for the tweets
    """
    client = pymongo.MongoClient(hostname)
    tweet_db = getattr(client, db_name)
    tweet_collection = getattr(tweet_db, collection_name)
    return tweet_collection


def extract_new_data(time_last_pull, hostname):
    """
    get a list of recent tweet jsons from a mongodb database
    time_last_pull is a timestamp representing the last time data was extracted
    """
    LOG.debug('Connecting to mongo')
    client = pymongo.MongoClient(hostname)
    tweet_db = client.tweet_db
    tweets = tweet_db.tweets
    LOG.debug('making request to mongo for tweets after %s',
              time_last_pull)
    extraction_result = tweets.find({'mongo_entry_ts':
                                    {"$gt": time_last_pull}})
    return list(extraction_result)


def get_user_data(tweet):
    """
    take a tweet json and extract the information relating to the tweet itself
    (as opposed to the user)
    """
    t = tweet
    current_user_data = {}
    current_user_data['user_id'] = t['user']['id']
    current_user_data['name'] = t['user']['name']
    current_user_data['screen_name'] = t['user']['screen_name']
    current_user_data['location'] = t['user']['location']
    current_user_data['verified'] = t['user']['verified']
    current_user_data['followers_count'] = t['user']['followers_count']
    current_user_data['favourites_count'] = t['user']['favourites_count']
    current_user_data['friends_count'] = t['user']['friends_count']
    current_user_data['statuses_count'] = t['user']['statuses_count']
    return current_user_data


def get_tweet_sentiment(tweet):
    """
    Take a tweet json, pass the text into vaderSentiment and return the
    sentiment
    """
    s = SentimentIntensityAnalyzer()
    tweet_text = tweet['text']
    if 'extended_tweet' in tweet:
        tweet_text = tweet['extended_tweet']['full_text']
    return s.polarity_scores(tweet_text)


def get_tweet_data(tweet):
    """
    take a tweet json and extract the information relating to the user
    """
    t = tweet
    current_tweet_data = {}
    current_tweet_data['tweet_id'] = t['id']
    current_tweet_data['favorited'] = t['favorited']
    current_tweet_data['favorite_count'] = t['favorite_count']
    current_tweet_data['quote_count'] = t['quote_count']
    current_tweet_data['retweet_count'] = t['retweet_count']
    current_tweet_data['reply_count'] = t['reply_count']
    current_tweet_data['timestamp_ms'] = t['timestamp_ms']
    try:
        current_tweet_data['place'] = t['place']['full_name']
    except (KeyError, TypeError):
        pass
    current_tweet_data["created_at"] = t["created_at"]
    current_tweet_data["user_id"] = t['user']['id']
    current_tweet_data['text'] = t['text']
    hashtags = t['entities']['hashtags']
    if 'extended_tweet' in t:
        current_tweet_data['text'] = t['extended_tweet']['full_text']
        hashtags = t['extended_tweet']['entities']['hashtags']

    # if 'retweeted_status' in t:
    #     r = t['retweeted_status']
    #     if 'extended_tweet' in r:
    #         current_tweet_data['text'] =  r['extended_tweet']['full_text']
    #         hashtags =  r['extended_tweet']['entities']['hashtags']

    current_tweet_data['hashtags'] = ', '.join([h['text'] for h in hashtags])
    current_tweet_data.update(get_tweet_sentiment(tweet))
    return current_tweet_data


def transform_data(data_list):
    """
    Take a list of tweet data extracted from mongo and transform it to a format
    that can be handled by sqlalchemy
    """
    LOG.debug('Transforming tweet data')
    transformed_data_list = []
    for item in data_list:
        tweet = item['tweet']
        transformed_item = {
            'tweet_id': tweet['id'],
            'key_word': item['key_words'],
            'mongo_entry_ts': item['mongo_entry_ts'],
            'user_data': get_user_data(tweet),
            'tweet_data': get_tweet_data(tweet)
        }
        transformed_data_list.append(transformed_item)
    return transformed_data_list


def extract_tweets(last_pull_time, host):
    """
    wrapper to run the extract_new_data function and update the time of the
    last data pull
    """
    LOG.debug('Trying to extract tweets from mongo')

    extracted_data = extract_new_data(last_pull_time, host)

    LOG.debug('First item from extracted tweet data: %s',
              extracted_data[-1])
    pull_time = time()
    return extracted_data, pull_time
