from sqlalchemy import BIGINT, Column, DateTime, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from .. import Base

class TCXLap(Base):
    __tablename__ = 'tcx_laps'

    id = Column(Integer, primary_key=True)
    total_time_seconds = Column(Float)
    distance_meters = Column(Float)
    maximum_speed = Column(Float)
    start_time = Column(DateTime)
    calories = Column(Float)
    average_bpm = Column(Integer)
    maximum_bpm = Column(Integer)
    activity_id = Column(BIGINT, ForeignKey('activities.id'))
    activity = relationship('Activity', back_populates='tcx_laps')
    track_points = relationship('TrackPoint', back_populates='lap')

    def __repr__(self):
        return f"<TCX Lap(id={self.id}, total_time_seconds={self.total_time_seconds}, distance_meters={self.distance_meters}, start_time={self.start_time}, calories={self.calories}, intensity={self.intensity}, triggered_method={self.triggered_method}, average_bpm={self.average_bpm}, maximum_bpm={self.maximum_bpm}, activity_id={self.activity_id})>"
