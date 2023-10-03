from datetime import datetime

from pydantic import BaseModel


class RecordBase(BaseModel):
    timestamp: datetime
    position_lat: float | None
    position_long: float | None
    distance: float | None
    altitude: float | None
    enhanced_speed: float | None
    enhanced_altitude: float | None
    vertical_oscillation: float | None
    stance_time_percent: float | None
    stance_time: float | None
    vertical_ratio: float | None
    stance_time_balance: float | None
    step_length: float | None
    heart_rate: int | None
    cadence: int | None
    activity_id: int


class Record(RecordBase):
    id: int

    class Config:
        orm_mode = True
