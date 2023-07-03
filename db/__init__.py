from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'mysql+mysqlconnector://usr:pswd@localhost:3306/stridze',
)
Base = declarative_base()

from .models import *

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_session():
    return SessionLocal()