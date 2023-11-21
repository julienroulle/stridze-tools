import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Replace the placeholders with your actual database information
# Detect platform to set the environment
# environ = "DEV"
environ = "DEV"

# Load the stored environment variables
load_dotenv(find_dotenv())

# Get the values
username = os.getenv(f"{environ}_DATABASE_USERNAME")
password = os.getenv(f"{environ}_DATABASE_PASSWORD")
host = os.getenv(f"{environ}_DATABASE_HOST")
port = os.getenv(f"{environ}_DATABASE_PORT")
database = os.getenv(f"{environ}_DATABASE_NAME")

# Construct the connection URL
connection_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

# Create the database engine
engine = create_engine(connection_url, poolclass=QueuePool)

# Base = declarative_base()

# from stridze.db.models import *

# Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_session():
    return SessionLocal()
