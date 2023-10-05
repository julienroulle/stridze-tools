from datetime import datetime

from pydantic import BaseModel


class StravaSchema(BaseModel):
    timestamp: datetime
    temperature: int
    moving: bool
    latitude: float
    longitude: float
    speed: float
    grade: float
    cadence: float | None
    distance: float
    heartrate: float
    elevation: float
    activity_id: int
    user_id: int
    activity_type: str


class Strava(StravaSchema):
    id: int

    class Config:
        orm_mode = True
