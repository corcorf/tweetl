"""
Module containing the python logging settings for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()


def set_up_log(level=None, name="tweetl",
               log_filename="tweetl.log",
               log_path=""):
    """
    Set up the python logging module
    return the log object
    """
    log = logging.getLogger(name)
    log_filename = os.path.join(log_path, log_filename)
    handler = logging.FileHandler(log_filename, mode='a')
    fmt = '%(asctime)s %(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    log.addHandler(handler)
    if level.upper() in ["DEBUG", "ERROR", "WARNING", "INFO", "CRITICAL"]:
        log.setLevel(getattr(logging, level.upper()))
        log.info("Logging level set to %s", getattr(logging, level.upper()))
    else:
        log.setLevel(logging.INFO)
        log.info("Logging level set to INFO")
    return log
