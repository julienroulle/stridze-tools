from pydantic import BaseModel

class TrackPointSchema(BaseModel):
    time: str
    altitude: float
    distance: float
    latitude: float
    longitude: float
    heart_rate: int
    speed: float
    cadence: int

    class Config:
        orm_mode = True
