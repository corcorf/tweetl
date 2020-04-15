"""
Module containing all SQL alchemy-based operations for the tweetl package
Python logging level can be set with the environment variable LOGGING_LEVEL
"""
import os
import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean, DateTime,
                        BigInteger, Float)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.inspection import inspect

load_dotenv()
LOG = logging.getLogger('tweetl.sql_operations')

HOST = 'localhost'
PORT = '5432'
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PGPASSWORD')
DB = os.getenv("PG_DB_NAME")
CONN_STRING = f'postgres://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'

ENGINE = create_engine(CONN_STRING, echo=False)
SESSION = sessionmaker(bind=ENGINE)
BASE = declarative_base()


class UserData(BASE):
    __tablename__ = 'user_data'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    screen_name = Column(String)
    location = Column(String)
    verified = Column(Boolean)
    followers_count = Column(Integer)
    favourites_count = Column(Integer)
    friends_count = Column(Integer)
    statuses_count = Column(Integer)
    time_created_mongo = Column(Float)
    time_created_sql = Column(DateTime(timezone=True),
                              server_default=func.now())

    tweets = relationship('TweetData', back_populates="user")

    def __repr__(self):
        return f'UserData {self.id}'


class TweetData(BASE):
    __tablename__ = 'tweet_data'
    id = Column(BigInteger, primary_key=True)
    favorited = Column(Boolean)
    favorite_count = Column(Integer)
    quote_count = Column(Integer)
    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    timestamp_ms = Column(BigInteger)
    coordinates = Column(String)
    place = Column(String)
    created_at = Column(DateTime)
    text = Column(String)
    hashtags = Column(String)
    time_created_sql = Column(DateTime(timezone=True),
                              server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('user_data.id'))
    sentiment_negativity = Column(Float)
    sentiment_neutrality = Column(Float)
    sentiment_positivity = Column(Float)
    sentiment_compound = Column(Float)

    user = relationship('UserData', back_populates="tweets")
    keywords = relationship("KeywordMatches", back_populates="tweet")

    def __repr__(self):
        return f'TweetData {self.id}'


class KeywordMatches(BASE):
    __tablename__ = 'keyword_matches'
    id = Column(Integer, primary_key=True)
    keywords = Column(String)
    tweet_id = Column(BigInteger, ForeignKey('tweet_data.id'))
    time_created_sql = Column(DateTime(timezone=True),
                              server_default=func.now())

    tweet = relationship('TweetData', back_populates="keywords")

    def __repr__(self):
        return f'KeywordMatches {self.id}'


def get_conn_string(host='localhost', port=5432, username=os.getenv('USER'),
                    password=os.getenv('PGPASSWORD'),
                    db=os.getenv("PG_DB_NAME")):
    """
    Return a sql connection string suitable for use by sqlalchemy
    """
    return f'postgres://{username}:{password}@{host}:{port}/{db}'


def create_tables(conn_string, echo=False):
    """
    Create the defined tables in a database defined by the conn_string if they
    don't already exist
    """
    engine = create_engine(conn_string, echo=echo)
    BASE.metadata.create_all(engine)


def check_for_duplicates(entry, table, session):
    """
    Return True if an entry with the same primary key already exists in the
    table
    """
    pk_tuple = table.__mapper__.primary_key
    pk_names = [pk.name for pk in pk_tuple]
    try:
        new_values = {name: entry[name] for name in pk_names}
    except KeyError as e:
        new_values = {}
        LOG.info('\nEntry %s has no value %s\n', entry, e)
    return bool([val for val in session.query(table).filter_by(**new_values)])


def write_to_table(data_dict, table_object, session):
    """
    accept a dictionary containing data and pass into an sqlalchemy table
    object return None
    """
    LOG.debug('Writing data to table')
    if not check_for_duplicates(data_dict, table_object, session):
        t = table_object(**data_dict)
        session.add(t)
        session.flush()
        session.commit()


def write_to_tweet_database(transformed_data_list, conn_string, echo=False):
    """
    take a list of transformed tweet data and enter everything into an sql
    database returns None
    """
    LOG.debug('Writing tweet to database')
    create_tables(conn_string, echo=echo)
    engine = create_engine(conn_string, echo=echo)
    session = sessionmaker(bind=engine)()

    for transformed_item in transformed_data_list:
        current_user_data = transformed_item['user_data']
        current_tweet_data = transformed_item['tweet_data']
        keyword = transformed_item['key_word'][0]
        LOG.debug('keyword: %s', keyword)
        kw_tweet_pair = {'tweet_id': current_tweet_data['id'],
                         'keywords': keyword}

        write_to_table(current_user_data, UserData, session)
        write_to_table(current_tweet_data, TweetData, session)
        write_to_table(kw_tweet_pair, KeywordMatches, session)


def one_or_more_results(query):
    """
    Return True if query contains one or more results, otherwise False
    """
    try:
        query.one()
    except NoResultFound:
        return False
    except MultipleResultsFound:
        pass
    return True


def get_tweets_since(since_datetime, conn_string,
                     table=TweetData,
                     datetime_col="timestamp_ms", echo=False):
    """
    Retrieve all tweets since since_datetime
    Return as a dataframe
    """
    engine = create_engine(conn_string, echo=echo)
    session = sessionmaker(bind=engine)()
    since_timestamp_ms = since_datetime.timestamp() * 1000
    query = session.query(table)\
                   .filter(getattr(table, datetime_col) >= since_timestamp_ms)
    if one_or_more_results(query):
        output_cols = [c.name for c in inspect(table).columns]
        result = query.values(*output_cols)
        result = pd.DataFrame(result)
        result = result.sort_values(by=datetime_col)
    else:
        result = None
    return result


def get_tweets_between(start_datetime, end_datetime, conn_string,
                       table=TweetData, keywords=None, keywords_col="text",
                       datetime_col="timestamp_ms", echo=False):
    """
    Retrieve all tweets in the db posted between start_datetime and
    end_datetime, optionally filtered by keywords
    Return as a dataframe
    """
    engine = create_engine(conn_string, echo=echo)
    session = sessionmaker(bind=engine)()
    start_timestamp_ms = start_datetime.timestamp() * 1000
    end_timestamp_ms = end_datetime.timestamp() * 1000
    query = session.query(table)\
                   .filter(getattr(table, datetime_col) >= start_timestamp_ms)\
                   .filter(getattr(table, datetime_col) < end_timestamp_ms)
    if isinstance(keywords, str):
        # query = query.subquery()
        ...
    if one_or_more_results(query):
        output_cols = [c.name for c in inspect(table).columns]
        result = query.values(*output_cols)
        result = pd.DataFrame(result)
        result = result.sort_values(by=datetime_col)
    else:
        result = None
    return result



# def get_tweets_for_time_window(start_time, end_time, search_term, conn_string):
#     """
#     """
#     engine = create_engine(conn_string, echo=False)
#     tweets = TweetData
#     s = tweets.select(
#             and_(tweets.c.created_at > start_time,
#                  tweets.c.text.like(f'%{search_term}%'))
#         )
#     #run(s)func.lower(User.username)
#     result = engine.execute(s)
#     result = result.fetchall()
#     return result
