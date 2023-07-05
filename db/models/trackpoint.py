from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .. import Base

class TrackPoint(Base):
    __tablename__ = 'track_points'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    altitude = Column(Float)
    distance = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    heart_rate = Column(Integer)
    speed = Column(Float)
    cadence = Column(Integer)
    lap_id = Column(Integer, ForeignKey('tcx_laps.id'))
    lap = relationship('TCXLap', back_populates='track_points')

    def __repr__(self):
        return f"<TrackPoint(id={self.id}, time={self.time}, altitude={self.altitude}, distance={self.distance}, latitude={self.latitude}, longitude={self.longitude}, heart_rate={self.heart_rate}, lap_id={self.lap_id})>"
