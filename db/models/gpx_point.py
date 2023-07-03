from sqlalchemy import BIGINT, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from .. import Base


# class GPXTrack(Base):
#     __tablename__ = 'gpx_tracks'

#     id = Column(Integer, primary_key=True)
#     name = Column(String(255))
#     user_id = Column(Integer, ForeignKey('users.id'))

#     user = relationship('User', back_populates='tracks')
#     points = relationship('GPXPoint', back_populates='track')

#     def __repr__(self):
#         return f"<GPXTrack(id={self.id}, name={self.name})>"


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