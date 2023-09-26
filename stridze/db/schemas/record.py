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
    vertical_oscillation: float
    stance_time_percent: float
    stance_time: float
    vertical_ratio: float
    stance_time_balance: float
    step_length: float
    heart_rate: int
    cadence: int
    activity_id: int


class Record(RecordBase):
    id: int

    class Config:
        orm_mode = True
