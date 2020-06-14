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

from tweetl.sql_operations import get_conn_string, create_tables
from tweetl.etl import etl_round
from tweetl.slack_bot import message_task

LOG = logging.getLogger('tweetl.etl')

load_dotenv()

MONGO_HOSTNAME = os.getenv('MONGO_CONTAINER_NAME')
SQL_CONN_STRING = get_conn_string(
    host=os.getenv('PG_CONTAINER_NAME'),
    port=5432,
    username=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    db=os.getenv('PG_DB_NAME'),
)
KEY_WORDS = os.getenv("KEY_WORDS")
FREQ = int(os.getenv('ETL_FREQUENCY', default=300))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'concurrency': 1,
    'retries': 2,
    # 'schedule_interval': f"0/{FREQ//60} * * * *",
    'catchup': False,
}


def create_postgres_db():
    """
    Wrapper for tweet.sql_operations.create_tables
    """
    create_tables(SQL_CONN_STRING, echo=False)


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
    'create_postgres_db',
    description="Creates Postgres DB for tweets if it doesn't already exist",
    schedule_interval="@once",
    default_args=default_args
) as create_pgdb_dag:

    create_db = PythonOperator(
        task_id='create_db', python_callable=create_postgres_db,
        dag=create_pgdb_dag
    )
    create_db.doc_md = """\
    #### CREATE PGDB
    Creates a database in Postgres for the transformed tweet data, \
    if one does not already exist
    """

    create_db


with DAG(
    'tweetl_dag',
    description='Performs ETL round and triggers slackbot',
    schedule_interval=timedelta(seconds=FREQ),
    catchup=False,
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
        task_id='slackbot', python_callable=run_slackbot, dag=tweetl_dag
    )
    slackbot.doc_md = """\
    #### SLACKBOT TASK
    - Post a message summarising the sentiment of tweets processed in the
    preceding ETL round
    """

    etl >> slackbot
