from datetime import datetime
from pydantic import BaseModel

class RecordBase(BaseModel):
    timestamp: datetime
    position_lat: float
    position_long: float
    distance: float
    altitude: float
    enhanced_altitude: float
    speed: float
    enhanced_speed: float
    heart_rate: int
    cadence: int
    activity_id: int


class Record(RecordBase):
    id: int

    class Config:
        orm_mode = True