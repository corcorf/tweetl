from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import os

Base = declarative_base()


def instantiate_tweet_tables(Base):
    """
    Pass an instance of declarative_base and get instances of the tables used
    in the tweets postgres database, namely UserData, TweetData, KeywordMatches
    """
    class UserData(Base):
        __tablename__ = 'user_data'
        user_id = Column(Integer, primary_key=True)
        name = Column(String)
        screen_name = Column(String)
        location = Column(String)
        verified = Column(Boolean)
        followers_count = Column(Integer)
        favourites_count = Column(Integer)
        friends_count = Column(Integer)
        statuses_count = Column(Integer)
        time_created_sql = Column(DateTime(timezone=True), server_default=func.now())

    #     tweets = relationship('TweetData', backref="tweets")

        def __repr__(self):
            return f'UserData {self.name}'

    # tweet_data
    class TweetData(Base):
        __tablename__ = 'tweet_data'
        tweet_id = Column(Integer, primary_key=True)
        favorited = Column(Boolean)
        favorite_count = Column(Integer)
        quote_count = Column(Integer)
        retweet_count = Column(Integer)
        reply_count = Column(Integer)
        timestamp_ms = Column(Integer)
        coordinates = Column(String)
        place = Column(String)
        created_at =Column(DateTime)
        text = Column(String)
        hashtags = Column(String)
        time_created_sql = Column(DateTime(timezone=True), server_default=func.now())

        user_id = Column(Integer, ForeignKey('user_data.user_id'), )
        user = relationship('UserData')

    #     def __repr__(self):
    #         return f'TweetData {self.name}'

    # keyword matches (keywords, tweet id)
    class KeywordMatches(Base):
        __tablename__ = 'keyword_matches'
        id = Column(Integer, primary_key=True)
        keywords = Column(String)
        tweet_id = Column(Integer, ForeignKey('tweet_data.tweet_id'))
        tweet = relationship('TweetData')
        time_created_sql = Column(DateTime(timezone=True), server_default=func.now())

        def __repr__(self):
            return f'KeywordMatches {self.name}'

    return UserData, TweetData, KeywordMatches
    #### NEED TO ADD USER DATA FIRST SO AS NOT TO VIOLATE FOREIGN KEY CONSTRAINTS
