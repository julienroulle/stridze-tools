from pydantic import BaseModel

class RecordBase(BaseModel):
    timestamp: float
    position_lat: float
    position_long: float
    distance: float
    altitude: float
    enhanced_altitude: float
    speed: float
    enhanced_speed: float
    heart_rate: int
    cadence: int
    lap_id: int


class Record(RecordBase):
    id: int

    class Config:
        orm_mode = True