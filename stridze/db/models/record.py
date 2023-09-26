from sqlalchemy import BIGINT, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .. import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    position_lat = Column(Float)
    position_long = Column(Float)
    distance = Column(Float)
    altitude = Column(Float)
    enhanced_speed = Column(Float)
    enhanced_altitude = Column(Float)
    vertical_oscillation = Column(Float)
    stance_time_percent = Column(Float)
    stance_time = Column(Float)
    vertical_ratio = Column(Float)
    stance_time_balance = Column(Float)
    step_length = Column(Float)
    heart_rate = Column(Integer)
    cadence = Column(Integer)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))

    activity = relationship("Activity", back_populates="records")

    def __repr__(self):
        return f"<Record(id={self.id}, record_id={self.lap_id})>"
