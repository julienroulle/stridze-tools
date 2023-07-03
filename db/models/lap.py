from sqlalchemy import BIGINT, Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from .. import Base

class Lap(Base):
    __tablename__ = 'laps'

    id = Column(Integer, primary_key=True)
    start_time = Column(Float)
    start_position_lat = Column(Float)
    start_position_long = Column(Float)
    total_elapsed_time = Column(Float)
    total_distance = Column(Float)
    total_calories = Column(Integer)
    avg_speed = Column(Float)
    max_speed = Column(Float)
    total_ascent = Column(Float)
    total_descent = Column(Float)
    avg_heart_rate = Column(Integer)
    max_heart_rate = Column(Integer)
    avg_cadence = Column(Integer)
    max_cadence = Column(Integer)
    avg_power = Column(Integer)
    max_power = Column(Integer)
    activity_id = Column(BIGINT, ForeignKey('activities.id'))

    activity = relationship('Activity', back_populates='laps')
    
    def __repr__(self):
        return f"<Lap(id={self.id}, activity_id={self.activity_id})>"
