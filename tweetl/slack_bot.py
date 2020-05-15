"""
Slack bot for sending information about collected tweets to
messaging service
"""

import os
import time
from datetime import datetime, timedelta
import logging

import numpy as np
import slack

from tweetl.sql_operations import get_conn_string, get_tweets_since

LOG = logging.getLogger('tweetl.slack_bot')


def get_slack_message(search_term, datetime, tweet_df):
    """
    """
    template = "Mean compound sentiment score for tweets about {}\
     since {}: {:.2f}"
    try:
        message = template.format(search_term, datetime.strftime('%H:%M'),
                                  np.nanmean(tweet_df['sentiment_compound']))
    except (TypeError, KeyError) as e:
        message = f"No tweets in db since {datetime.strftime('%H:%M')}"
        LOG.debug(
            "Error retrieving sentiments since %s for slack message: %s",
            datetime, e
        )
    return message


def extract_args(args):
    """
    Take arguments from tweetl cli and process arguments needed for slackbot
    args should be an argparse namespace object including the following fields:
        freq (integer): time in seconds to wait between slack_bot reports
        postgres_hostname (string): name of host running postgresql instance
    Returns freq, sql_conn_string, search_term
    """
    freq = args.freq
    sql_conn_string = get_conn_string(
        host=args.pg_hostname,
        port=args.pg_port,
        username=args.pg_user,
        password=args.pg_password,
        db=args.pg_database,
    )
    search_term = args.key_words
    return freq, sql_conn_string, search_term


def get_client(env_var="SLACK_TOKEN"):
    """
    Get a slack client using a slack token held as an environment
    variable with the name given in env_var
    """
    oauth_access_token = os.getenv(env_var)
    return slack.WebClient(token=oauth_access_token)


def post_message(since_datetime, sql_conn_string, search_term,
                 slack_client, slack_channel):
    """
    Post a message to the slack channel
    """
    tweets = get_tweets_since(since_datetime, sql_conn_string)
    message = get_slack_message(search_term, since_datetime, tweets)
    response = slack_client.chat_postMessage(channel=slack_channel,
                                             text=message)
    LOG.debug(response)


def main(args):
    """
    Run slack bot with arguments from command line
    args should be an argparse namespace object including the following fields:
        freq (integer): time in seconds to wait between slack_bot reports
        postgres_hostname (string): name of host running postgresql instance
    """
    freq, sql_conn_string, search_term = extract_args(args)
    client = get_client()
    channel = "#flanns_slackbot_test"

    while True:
        since_datetime = datetime.now() - timedelta(0, freq)
        post_message(since_datetime, sql_conn_string, search_term,
                     client, channel)
        time.sleep(freq)
