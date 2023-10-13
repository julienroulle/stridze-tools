from pydantic import BaseModel


class ActivityBase(BaseModel):
    id: int
    user_id: int
    elapsed_time: int | None
    moving_time: int | None
    distance: int
    elevation_gain: int | None
    elevation_loss: int | None
    average_pace: int | None
    average_moving_pace: int | None
    average_cadence: int | None
    average_heart_rate: int | None
    max_heart_rate: int | None
    average_stride_length: float | None
    average_temperature: float | None
    calories: int | None


class Activity(ActivityBase):
    id: int

    class Config:
        orm_mode = True
