"""
Module defining a Tweepy StreamListener for collecting tweets featuring one or
more keywords and adding them to a MongoDB collection
Requires Twitter API credentials to be define as environment variables with the
following names: CONSUMER_API_KEY, CONSUMER_API_SECRET
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import os
import json
from time import time
import argparse
import logging

from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
from dotenv import load_dotenv

from tweetl.mongo_operations import get_tweet_collection

load_dotenv()
LOG = logging.getLogger('tweetl.get_tweets')


class TwitterListener(StreamListener):
    """
    Listener for intercepting tweets
    """
    def __init__(self, keywords, collection, *args):
        """
        add list of keywords and pymongo connection to a mongodb collection to
        StreamListener attributes
        """
        self.keywords = keywords
        self.collection = collection
        StreamListener.__init__(self, *args)

    def on_data(self, data):
        """
        Whatever we put in this method defines what is done with
        every single tweet as it is intercepted in real-time
        """
        tweet_content = json.loads(data)
        text = tweet_content.get("text")

        if 'extended_tweet' in tweet_content:
            text = tweet_content['extended_tweet']['full_text']
        if 'retweeted_status' in tweet_content:
            r = tweet_content['retweeted_status']
            if 'extended_tweet' in r:
                text = r['extended_tweet']['full_text']

        if text is not None:
            LOG.info('\nTWEET INCOMING: %s\n', text)
        else:
            LOG.info('\nAPI MESSAGE: %s\n', tweet_content)

        entry = {'key_words': self.keywords,
                 'tweet': tweet_content,
                 'mongo_entry_ts': time()}
        self.collection.insert_one(entry)

    def on_error(self, status):
        """
        actions to perform if the API raises and error
        """
        if status == 420:
            LOG.warning(status)
            return False


def authenticate():
    """
    Return OAuth handler for access to Twitter API
    CONSUMER_API_KEY and CONSUMER_API_SECRET must be defined as environment
    variables.
    """
    LOG.info('authenticating')
    auth = OAuthHandler(os.getenv("CONSUMER_API_KEY"),
                        os.getenv("CONSUMER_API_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"),
                          os.getenv("ACCESS_TOKEN_SECRET"))
    return auth


def get_arguments():
    """
    Get keywords as arguments from the command line
    """
    LOG.debug("fetching arguments")
    description = 'Set up a Tweepy StreamListener to gather tweets based on \
    specified keywords.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--hostname", dest='hostname', type=str, nargs='?',
                        default="",
                        help='Specify the MongoDB hostname')
    parser.add_argument(dest='key_words', type=str, nargs='*',
                        help='Keywords that collected tweets will include')
    return parser.parse_args()


def main():
    """
    Set up TwitterListener to listen for tweets containing one or more of
    key_words (list)
    The TwitterListener sends the tweet data directly to a mongodb collection
    """
    args = get_arguments()

    if not args.hostname:
        hostname = os.getenv("MONGO_CONTAINER_NAME", default="mongodb")
    else:
        hostname = args.hostname

    if not args.key_words:
        key_words = os.getenv("KEYWORDS")
    else:
        key_words = args.key_words

    LOG.info('Hostname: %s', hostname)
    LOG.info('Keywords: %s', key_words)
    tweet_collection = get_tweet_collection(hostname=hostname)

    auth = authenticate()
    LOG.info('instantiating listener')
    listener = TwitterListener(key_words, tweet_collection)

    LOG.info('starting stream')
    stream = Stream(auth, listener)
    stream.filter(track=key_words, languages=['en'])


if __name__ == '__main__':
    main()
