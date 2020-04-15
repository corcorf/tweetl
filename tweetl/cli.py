"""
Command line interface for tweetl package
"""
import sys
import argparse


def add_etl_args(parser):
    """
    Add arguments to the parser that are used by the etl job
    """
    parser.add_argument(
        "-f", "--freq", type=int, default=300,
        help='frequency at which etl rounds are conducted (in seconds)'
    )
    return parser


def add_tweet_search_args(parser):
    """
    Add arguments to the parser that are used by the tweet search
    """
    parser.add_argument(
        "-k", "--key_words", nargs="+", type=str,
        help='Keywords to be used by get_tweets (ignored for etl)'
    )
    return parser


def add_postgres_args(parser):
    """
    Add arguments to the parser that are used for connecting to a postgres
    server
    """
    parser.add_argument(
        "-o", "--pg_hostname", type=str, default="localhost",
        help='Specify the PostGreSQL hostname'
    )
    parser.add_argument(
        "-d", "--pg_database", type=str, default="postgres",
        help='Specify the PostGreSQL database name'
    )
    parser.add_argument(
        "-p", "--pg_port", type=int, default=5432,
        help='Specify the PostGreSQL port number'
    )
    parser.add_argument(
        "-u", "--pg_user", type=str, default="postgres",
        help='Specify the PostGreSQL user name'
    )
    parser.add_argument(
        "-w", "--pg_password", type=str, default="postgres",
        help='Specify the PostGreSQL password'
    )
    return parser


def add_mongo_args(parser):
    """
    Add arguments to the parser that are used by all functions
    """
    parser.add_argument(
        "-m", "--mongo_hostname", type=str, default="mongodb",
        help='Specify the MongoDB hostname'
    )
    return parser


def get_arguments():
    """
    Get arguments for all tweetl submodules, including from which submodule
    the main script should be run
    """
    description = 'Specify which tweetl submodule should be run and the\
     arguments that it should take.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'module', type=str,
        help='tweetl module to be run (get_tweets or etl)'
    )
    parser = add_mongo_args(parser)
    parser = add_postgres_args(parser)
    parser = add_tweet_search_args(parser)
    parser = add_etl_args(parser)
    return parser.parse_args()


def get_tweet_search_arguments():
    """
    Get keywords as arguments from the command line
    """
    description = 'Set up a Tweepy StreamListener to gather tweets based on \
    specified keywords.'
    parser = argparse.ArgumentParser(description=description)
    parser = add_mongo_args(parser)
    parser = add_tweet_search_args(parser)
    return parser.parse_args()


def get_etl_arguments():
    """
    Get keywords as arguments from the command line
    """
    description = 'Set up an ETL job for moving collected tweel data from\
     mongodb to postgres at a specified frequency.'
    parser = argparse.ArgumentParser(description=description)
    parser = add_mongo_args(parser)
    parser = add_postgres_args(parser)
    parser = add_etl_args(parser)
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(get_arguments())  # pragma: no cover
