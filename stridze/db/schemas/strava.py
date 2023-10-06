from datetime import datetime

from pydantic import BaseModel


class StravaSchema(BaseModel):
    timestamp: datetime
    temperature: int | None
    moving: bool | None
    latitude: float
    longitude: float
    speed: float | None
    grade: float | None
    cadence: float | None
    distance: float
    heartrate: float | None
    elevation: float | None
    activity_id: int
    user_id: int
    activity_type: str


class Strava(StravaSchema):
    id: int

    class Config:
        orm_mode = True
