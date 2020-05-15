"""
Module containing the extract-transform-load job for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import logging
from time import sleep

from dotenv import load_dotenv

from tweetl.mongo_operations import extract_new_data, transform_data
from tweetl.sql_operations import (write_to_tweet_database, get_conn_string,
                                   get_last_mongo_time)
from tweetl.cli import get_etl_arguments

load_dotenv()

LOG = logging.getLogger('tweetl.etl')


def etl_round(mongo_hostname, sql_conn_string):
    """
    Do an etl round
    return the time
    """
    last_pull_time = get_last_mongo_time(sql_conn_string)
    extracted = extract_new_data(last_pull_time, mongo_hostname)
    transformed = transform_data(extracted)
    write_to_tweet_database(transformed, sql_conn_string)
    LOG.debug('etl_round_done')


def main(args):
    """
    Run etl job with arguments from command line
    args should be an argparse namespace object including the following fields:
        freq (integer): time in seconds to wait between etl rounds
        mongo_hostname (string): name of host running mongodb instance
        postgres_hostname (string): name of host running postgresql instance
    """
    last_pull_time = 0
    LOG.debug('Initialising pull time: %s', last_pull_time)
    freq = args.freq
    mongo_hostname = args.mongo_hostname

    sql_conn_string = get_conn_string(
        host=args.pg_hostname,
        port=args.pg_port,
        username=args.pg_user,
        password=args.pg_password,
        db=args.pg_database,
    )

    while True:
        etl_round(
            mongo_hostname, sql_conn_string
        )
        sleep(freq)


if __name__ == "__main__":
    args = get_etl_arguments()
    main(args)
