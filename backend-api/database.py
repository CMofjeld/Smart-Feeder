"""Database connection for API."""
import os

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

## Disable pooling in pyodbc
pyodbc.pooling = False 

## Create database engine
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")
connection_string = 'DRIVER='+DB_DRIVER+';SERVER=tcp:'+DB_SERVER+';PORT=1433;DATABASE='+DB_NAME+';UID='+DB_USERNAME+';PWD='+DB_PASSWORD
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url)

## Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False) # why autoflush=False?

## ORM classes
# Create base class to inherit from
Base = declarative_base()
