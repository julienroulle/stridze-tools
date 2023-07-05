from sqlalchemy import BIGINT, Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .. import Base

class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    position_lat = Column(Float)
    position_long = Column(Float)
    distance = Column(Float)
    altitude = Column(Float)
    enhanced_altitude = Column(Float)
    speed = Column(Float)
    enhanced_speed = Column(Float)
    heart_rate = Column(Integer)
    cadence = Column(Integer)
    activity_id = Column(BIGINT, ForeignKey('activities.id'))

    activity = relationship('Activity', back_populates='records')

    def __repr__(self):
        return f"<Record(id={self.id}, lap_id={self.lap_id})>"