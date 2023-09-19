from contextlib import contextmanager
from db.controllers import create_activity, create_user, get_user, get_db_size
from db.models import GPXPoint, Lap, Record, TCXLap, TrackPoint
from db.schemas.activity import ActivityBase
from db.schemas.user import UserBase
from db import get_session

from functools import reduce
import gpxpy
import fitdecode
from lxml import objectify
import os
import pandas as pd
import sqlalchemy

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        
def calculate_pace(time_seconds, distance_meters):
    # Convert distance to kilometers
    distance_km = distance_meters / 1000
    
    # Convert time to minutes
    time_minutes = time_seconds / 60
    
    # Calculate pace
    pace = time_minutes / distance_km
    
    return pace

def process_gpx_files(activity_id, session):
    # Your code for processing GPX files here

def process_fit_files(activity_id, session):
    # Your code for processing FIT files here

def process_tcx_files(activity_id, session):
    # Your code for processing TCX files here

def main():
    user = UserBase(first_name="Julien", last_name="Roullé", email="ju.roulle@gmail.com", password="Julien35830")
    with session_scope() as session:
        # create_user(db=session, user=user)
        user = get_user(session, "ju.roulle@gmail.com")
        print(user.id)
        # get_user(db, 1)

    for activity_id in os.listdir('data/raw/'):
        if activity_id.endswith('.DS_Store'):
            continue

        with session_scope() as session:
            process_gpx_files(activity_id, session)
            process_fit_files(activity_id, session)
            process_tcx_files(activity_id, session)

if __name__ == "__main__":
    main()