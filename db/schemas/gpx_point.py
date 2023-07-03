from pydantic import BaseModel


class GPXPointBase(BaseModel):
    latitude: float
    longitude: float
    elevation: float
    activity_id: int


class GPXPoint(GPXPointBase):
    id: int

    class Config:
        orm_mode = True
