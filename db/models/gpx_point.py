from sqlalchemy import BIGINT, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from .. import Base

class GPXPoint(Base):
    __tablename__ = 'gpx_points'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    activity_id = Column(BIGINT, ForeignKey('activities.id'))

    activity = relationship('Activity', back_populates='points')

    def __repr__(self):
        return f"<GPXPoint(id={self.id}, latitude={self.latitude}, longitude={self.longitude}, elevation={self.elevation}, activity_id={self.activity_id})>"