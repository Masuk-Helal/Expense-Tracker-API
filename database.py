from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1234@localhost/ExpanceTrakerDatabase'

# if SQLALCHEMY_DATABASE_URL.startswith('postgres://'):
#     SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgres://', 'postgresql://', 1)

connect_args = {'check_same_thread': False} if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
