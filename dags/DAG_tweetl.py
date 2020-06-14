"""
Airflow DAG
"""

import os
import logging
from datetime import timedelta

from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from tweetl.sql_operations import get_conn_string
from tweetl.etl import etl_round
from tweetl.slack_bot import message_task

LOG = logging.getLogger('tweetl.etl')

load_dotenv(dotenv_path="/app/.env")

MONGO_HOSTNAME = os.getenv('MONGO_CONTAINER_NAME')
SQL_CONN_STRING = get_conn_string(
    host=os.getenv('PG_CONTAINER_NAME'),
    port=os.getenv('PG_PORT'),
    username=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    db=os.getenv('PG_DB_NAME'),
)
KEY_WORDS = os.getenv("KEY_WORDS")
FREQ = int(os.getenv('ETL_FREQUENCY'))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'concurrency': 1,
    'retries': 2,
    'schedule_interval': timedelta(seconds=FREQ),
    'catchup': False,
}


def etl_with_hostname():
    """
    Wrapped version of tweet.etl.etl_round with hostname taken from environment
    variables
    """
    etl_round(MONGO_HOSTNAME, SQL_CONN_STRING)


def run_slackbot():
    """
    Wrapper around the tweet.slack_bot.message_task function fro use in DAG
    """
    message_task(SQL_CONN_STRING, KEY_WORDS, FREQ)


with DAG(
    'tweetl_dag',
    description='Performs ETL round and triggers slackbot',
    default_args=default_args
) as tweetl_dag:

    etl = PythonOperator(
        task_id='ETL', python_callable=etl_with_hostname, dag=tweetl_dag
    )
    etl.doc_md = """\
    #### TWEETL ETL JOB
    - Extract tweets from MongoDB
    - Transform JSON-like documents to table structure, adding processing times
    and sentiment analysis scores
    - Load transformed tweets to PostgreSQL
    """

    slackbot = PythonOperator(
        task_id='transform', python_callable=run_slackbot, dag=tweetl_dag
    )
    slackbot.doc_md = """\
    #### SLACKBOT TASK
    - Post a message summarising the sentiment of tweets processed in the
    preceding ETL round
    """

    etl >> slackbot
