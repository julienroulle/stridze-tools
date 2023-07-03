from pydantic import BaseModel


class LapBase(BaseModel):
    start_time: float
    start_position_lat: float
    start_position_long: float
    total_elapsed_time: float
    total_distance: float
    total_calories: int
    avg_speed: float
    max_speed: float
    total_ascent: float
    total_descent: float
    avg_heart_rate: int
    max_heart_rate: int
    avg_cadence: int
    max_cadence: int
    avg_power: int
    max_power: int
    activity_id: int


class Lap(LapBase):
    id: int

    class Config:
        orm_mode = True