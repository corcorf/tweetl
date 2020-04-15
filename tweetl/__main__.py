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
        LOG.error("No keywords found.\
         Must supply keywords if using get_tweets module.\n")
    else:
        LOG.info("Running get_tweets module with args:\n%s", args)
        tweetl.get_tweets.main(args)
elif args.module == "slack_bot":
    if args.key_words is None:
        LOG.error("No keywords found.\
         Must supply keywords if using slack_bot module.\n")
    else:
        LOG.info("Running slack_bot module with args:\n%s", args)
        tweetl.slack_bot.main(args)
else:
    LOG.error("Unrecognised module name. Enter one of 'etl', 'get_tweets'\
     or 'slack_bot'.\n")
