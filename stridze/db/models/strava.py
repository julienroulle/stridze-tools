from sqlalchemy import BIGINT, Boolean, Column, DateTime, Float, Integer

from .. import Base


class Strava(Base):
    __tablename__ = "strava"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    temperature = Column(Integer)
    moving = Column(Boolean)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    grade = Column(Float)
    cadence = Column(Float)
    distance = Column(Float)
    heartrate = Column(Float)
    elevation = Column(Float)
    activity_id = Column(BIGINT)
    user_id = Column(BIGINT)
