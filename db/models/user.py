from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .. import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(32))
    last_name = Column(String(32))
    email = Column(String(32), unique=True, index=True, nullable=False)
    password = Column(String(32))
    vdot = Column(Integer)

    activities = relationship('Activity', back_populates='user')