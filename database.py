from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:1234@127.0.0.1:3306/ExpanceTrakerDatabase'


# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# if not SQLALCHEMY_DATABASE_URL:
#     raise RuntimeError("DATABASE_URL is not configured")

# connect_args = {}

# if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
#     connect_args = {"check_same_thread": False}


# connect_args = {'check_same_thread': False} if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
