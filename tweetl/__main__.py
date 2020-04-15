"""
tweetl main module
"""
import logging
import tweetl

LOG = logging.getLogger('tweetl.main')

args = tweetl.cli.get_arguments()
if args.module == "etl":
    LOG.info("Running etl module with args:\n%s", args)
    tweetl.etl.main(args)
elif args.module == "get_tweets":
    if args.key_words is None:
        LOG.info("Running get_tweets module with args:\n%s", args)
        LOG.error("No keywords found.\
         Must supply keywords if using get_tweets module.\n")
    else:
        tweetl.get_tweets.main(args)
else:
    LOG.error("Unrecognised module name. Enter either 'etl' or 'get_tweets'.\
    \n")
