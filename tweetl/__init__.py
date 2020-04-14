"""
Initialise log for module
"""
import os
from dotenv import load_dotenv
from tweetl.tweetl_log import set_up_log

load_dotenv()

LOG = set_up_log(level=os.getenv("LOGGING_LEVEL"),
                 name="tweetl",
                 log_filename="{}_tweetl.log".format(
                     os.getenv("CONTAINER_NAME"),
                 ),
                 log_path=os.getenv("CONTAINER_LOG_PATH", default=""))
