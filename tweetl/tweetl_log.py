"""
Module containing the python logging settings for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()


def set_up_log(level=os.getenv("LOGGING_LEVEL"),
               name="tweetl",
               log_filename="{}_tweetl.log".format(
                   os.getenv("CONTAINER_NAME"),
               ),
               log_path=os.getenv("CONTAINER_LOG_PATH", default="")):
    """
    Set up the python logging module
    return the log object
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)

    log_filename = os.path.join(log_path, log_filename)
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setFormatter(formatter)
    if level.upper() in ["DEBUG", "ERROR", "WARNING", "INFO", "CRITICAL"]:
        file_handler.setLevel(getattr(logging, level.upper()))
    else:
        file_handler.setLevel(logging.INFO)

    log.addHandler(console_handler)
    log.addHandler(file_handler)

    return log
