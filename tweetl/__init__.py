"""
Initialise log for module
"""
import os
from dotenv import load_dotenv

import cli
import etl
import get_tweets
import mongo_operations
import sql_operations
import tweetl_log

load_dotenv()

LOG = tweetl_log.set_up_log(level=os.getenv("LOGGING_LEVEL"),
                            name="tweetl",
                            log_filename="{}_tweetl.log".format(
                             os.getenv("CONTAINER_NAME"),
                            ),
                            log_path=os.getenv("CONTAINER_LOG_PATH",
                                               default="")
                            )
