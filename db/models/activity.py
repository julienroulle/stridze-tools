from sqlalchemy import BIGINT, Column, Float, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import relationship

from .. import Base
    
class Activity(Base):
    __tablename__ = "activities"

    id = Column(BIGINT, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    elapsed_time = Column(Integer, nullable=True)
    moving_time = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)
    elevation_gain = Column(Integer, nullable=True)
    elevation_loss = Column(Integer, nullable=True)
    average_pace = Column(Integer, nullable=True)
    average_moving_pace = Column(Integer, nullable=True)
    average_cadence = Column(Integer, nullable=True)
    average_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    average_stride_length = Column(Float(precision=8, asdecimal=True), nullable=True)
    average_temperature = Column(Float(precision=8, asdecimal=True), nullable=True)
    calories = Column(Integer, nullable=True)

    user = relationship('User', back_populates='activities')
    points = relationship('GPXPoint', back_populates='activity')

    def __repr__(self):
        return f"<Activity(id={self.id}, user_id={self.user_id})>"