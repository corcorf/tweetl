import logging
import time
import pymongo
from sqlalchemy import create_engine
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import os

logging.basicConfig(level=logging.DEBUG) #filename='debug.log'

def extract_new_data(time_last_pull, hostname):
    """
    get a list of recent tweet jsons from a mongodb database
    time_last_pull is a timestamp representing the last time data was extracted
    """
    logging.debug(f'Connecting to mongo')
    client = pymongo.MongoClient(hostname)
    tweet_db = client.tweet_db
    tweets = tweet_db.tweets

    logging.debug(f'making request to mongo for tweets after {time_last_pull}')
    extraction_result = tweets.find({'mongo_entry_ts':{"$gt":time_last_pull}})
    return list(extraction_result)


def get_user_data(tweet):
    """
    take a tweet json and extract the information relating to the tweet itself
    (as opposed to the user)
    """
    t = tweet
    current_user_data = {}
    current_user_data['user_id'] = t['user']['id']
    current_user_data['name'] = t['user']['name']
    current_user_data['screen_name'] = t['user']['screen_name']
    current_user_data['location'] = t['user']['location']
    current_user_data['verified'] = t['user']['verified']
    current_user_data['followers_count'] = t['user']['followers_count']
    current_user_data['favourites_count'] = t['user']['favourites_count']
    current_user_data['friends_count'] = t['user']['friends_count']
    current_user_data['statuses_count'] = t['user']['statuses_count']

    return current_user_data

def get_tweet_sentiment(tweet):
    """
    Take a tweet json, pass the text into vaderSentiment and return the sentiment
    """
    s = SentimentIntensityAnalyzer()

    tweet_text = tweet['text']
    if 'extended_tweet' in tweet:
        tweet_text =  tweet['extended_tweet']['full_text']

    return s.polarity_scores(tweet_text)

def get_tweet_data(tweet):
    """
    take a tweet json and extract the information relating to the user
    """
    t = tweet
    current_tweet_data = {}
    current_tweet_data['tweet_id'] = t['id']
    current_tweet_data['favorited'] = t['favorited']
    current_tweet_data['favorite_count'] = t['favorite_count']
    current_tweet_data['quote_count'] = t['quote_count']
    current_tweet_data['retweet_count'] = t['retweet_count']
    current_tweet_data['reply_count'] = t['reply_count']
    current_tweet_data['timestamp_ms'] = t['timestamp_ms']
    # current_tweet_data['geo'] = t['geo']
    #current_tweet_data['coordinates'] = t['coordinates']
    try:
        current_tweet_data['place'] = t['place']['full_name']
    except (KeyError, TypeError):
        pass
    current_tweet_data["created_at"] = t["created_at"]
    current_tweet_data["user_id"] = t['user']['id']

    current_tweet_data['text'] = t['text']
    hashtags =  t['entities']['hashtags']
    if 'extended_tweet' in t:
        current_tweet_data['text'] =  t['extended_tweet']['full_text']
        hashtags =  t['extended_tweet']['entities']['hashtags']

    # if 'retweeted_status' in t:
    #     r = t['retweeted_status']
    #     if 'extended_tweet' in r:
    #         current_tweet_data['text'] =  r['extended_tweet']['full_text']
    #         hashtags =  r['extended_tweet']['entities']['hashtags']

    current_tweet_data['hashtags']  =  ', '.join([h['text'] for h in hashtags])

    current_tweet_data.update(get_tweet_sentiment(tweet))

    return current_tweet_data


def transform_data(data_list):
    """
    Take a list of tweet data extracted from mongo and transform it to a format
    that can be handled by sqlalchemy
    """
    logging.debug(f'Transforming tweet data')
    transformed_data_list = []
    for item in data_list:
        tweet = item['tweet']

        transformed_item = {
        'tweet_id':tweet['id'],
        'key_word':item['key_words'],
        'mongo_entry_ts':item['mongo_entry_ts'],
        'user_data':get_user_data(tweet),
        'tweet_data':get_tweet_data(tweet)
        }

        transformed_data_list.append(transformed_item)
    return transformed_data_list

def instantiate_UserData_table(Base):
    """
    Takes an sqlalchemy declarative_base object and creates an sqlalchemy
    object for the pre-defined UserData table. If the table does not already exist in
    the database it will be created
    """
    logging.debug(f'Instantiating UserData table')
    class UserData(Base):
        __tablename__ = 'user_data'
        user_id = Column(BigInteger, primary_key=True)
        name = Column(String)
        screen_name = Column(String)
        location = Column(String)
        verified = Column(Boolean)
        followers_count = Column(Integer)
        favourites_count = Column(Integer)
        friends_count = Column(Integer)
        statuses_count = Column(Integer)
        time_created_sql= Column(DateTime(timezone=True), server_default=func.now())

    #     tweets = relationship('TweetData', backref="tweets")

        def __repr__(self):
            return f'UserData {self.name}'

    return UserData

def instantiate_TweetData_table(Base):
    """
    Takes an sqlalchemy declarative_base object and creates an sqlalchemy
    object for the pre-defined TweetData table. If the table does not already exist in
    the database it will be created
    """
    logging.debug(f'Instantiating TweetData table')
    class TweetData(Base):
        __tablename__ = 'tweet_data'
        tweet_id = Column(BigInteger, primary_key=True)
        favorited = Column(Boolean)
        favorite_count = Column(Integer)
        quote_count = Column(Integer)
        retweet_count = Column(Integer)
        reply_count = Column(Integer)
        timestamp_ms = Column(String)
        coordinates = Column(String)
        place = Column(String)
        created_at =Column(DateTime)
        text = Column(String)
        hashtags = Column(String)
        time_created_sql = Column(DateTime(timezone=True), server_default=func.now())
        ### columns for tweet sentiment
        neg = Column(Float)
        neu = Column(Float)
        pos = Column(Float)
        compound = Column(Float)

        user_id = Column(BigInteger, ForeignKey('user_data.user_id'), )
        user = relationship('UserData')

        def __repr__(self):
            return f'TweetData {self.name}'

    return TweetData

def instantiate_KeywordMatches_table(Base):
    """
    Takes an sqlalchemy declarative_base object and creates an sqlalchemy
    object for the pre-defined KeyWordMatches table. If the table does not already exist in
    the database it will be created
    """
    logging.debug(f'Instantiating KeywordMatches table')
    class KeywordMatches(Base):
        __tablename__ = 'keyword_matches'
        id = Column(BigInteger, primary_key=True)
        keywords = Column(String)
        tweet_id = Column(BigInteger, ForeignKey('tweet_data.tweet_id'))
        tweet = relationship('TweetData')
        time_created_sql = Column(DateTime(timezone=True), server_default=func.now())

        def __repr__(self):
            return f'KeywordMatches {self.name}'

    return KeywordMatches

def instantiate_tweet_tables(Base):
    """
    Pass in an instance of declarative_base and get instances of the tables used
    in the tweets postgres database, namely UserData, TweetData, KeywordMatches
    """
    logging.debug(f'Instantiating all tables')
    UserData = instantiate_UserData_table(Base)
    TweetData = instantiate_TweetData_table(Base)
    KeywordMatches = instantiate_KeywordMatches_table(Base)

    return UserData, TweetData, KeywordMatches

def check_for_duplicates(entry, table, session):
    """
    Return True if an entry with the same primary key already exists in the table
    """
    pk_tuple = table.__mapper__.primary_key
    pk_names = [pk.name for pk in pk_tuple]
    try:
        new_values = {name:entry[name] for name in pk_names}
    except KeyError as e:
        new_values = {}
        logging.info(f'\nEntry {entry} has no value {e}\n')

    return bool([val for val in session.query(table).filter_by(**new_values)])

def write_to_table(data_dict, table_object, session):
    """
    accept a dictionary containing data and pass into an sqlalchemy table object
    return None
    """
    logging.debug(f'Writing data to table')
    if not check_for_duplicates(data_dict, table_object, session):
        t = table_object(**data_dict)
        session.add(t)
        session.flush()
        session.commit()


def write_to_tweet_database(transformed_data_list, conn_string, echo=False):
    """
    take a list of transformed tweet data and enter everything into an sql database
    returns None
    """
    logging.debug(f'Writing tweet to database')
    engine = create_engine(conn_string, echo=echo)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
    UserData, TweetData, KeywordMatches = instantiate_tweet_tables(Base)
    logging.debug(f'Creating tables in sql')
    Base.metadata.create_all(engine)

    transformed_data_list

    for transformed_item in transformed_data_list:
        current_user_data = transformed_item['user_data']
        current_tweet_data = transformed_item['tweet_data']
        keyword = transformed_item['key_word'][0]
        logging.debug(f'keyword: {keyword}')
        kw_tweet_pair = {'tweet_id':current_tweet_data['tweet_id'],
                        'keywords':keyword}

        write_to_table(current_user_data, UserData, session)
        write_to_table(current_tweet_data, TweetData, session)
        write_to_table(kw_tweet_pair, KeywordMatches, session)
