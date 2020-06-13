"""
Initialise log for module
"""
import os
from dotenv import load_dotenv

import tweetl.cli
import tweetl.etl
import tweetl.get_tweets
import tweetl.mongo_operations
import tweetl.slack_bot
import tweetl.sql_operations
import tweetl.tweetl_log

load_dotenv()

LOG = tweetl.tweetl_log.set_up_log(
    level=os.getenv("LOGGING_LEVEL"),
    name="tweetl",
    log_filename=f"{os.getenv('CONTAINER_NAME')}_tweetl.log",
    log_path=os.getenv("CONTAINER_LOG_PATH", default="")
)
