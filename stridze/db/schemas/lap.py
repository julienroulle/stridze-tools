from datetime import datetime

from pydantic import BaseModel


class LapBase(BaseModel):
    start_time: datetime
    start_position_lat: float
    start_position_long: float
    total_elapsed_time: float
    total_distance: float
    total_calories: int
    avg_speed: float | None
    max_speed: float | None
    total_ascent: float
    total_descent: float
    avg_heart_rate: int | None
    max_heart_rate: int | None
    avg_cadence: int
    max_cadence: int
    avg_power: int | None
    max_power: int | None
    activity_id: int


class Lap(LapBase):
    id: int

    class Config:
        orm_mode = True
