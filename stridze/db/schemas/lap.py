from datetime import datetime

from pydantic import BaseModel


class LapBase(BaseModel):
    start_time: datetime
    start_position_lat: float | None
    start_position_long: float | None
    total_elapsed_time: float
    total_distance: float
    total_calories: int | None
    avg_speed: float | None
    max_speed: float | None
    total_ascent: float | None
    total_descent: float | None
    avg_heart_rate: int | None
    max_heart_rate: int | None
    avg_cadence: int | None
    max_cadence: int | None
    avg_power: int | None
    max_power: int | None
    activity_id: int


class Lap(LapBase):
    id: int

    class Config:
        orm_mode = True
