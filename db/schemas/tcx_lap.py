from pydantic import BaseModel

class TCXLapSchema(BaseModel):
    id: int
    total_time_seconds: float
    distance_meters: float
    maximum_speed: float
    start_time: str
    calories: float
    intensity: str
    triggered_method: str
    average_bpm: int
    maximum_bpm: int
    activity_id: int

    class Config:
        orm_mode = True
