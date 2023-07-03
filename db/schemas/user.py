from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    vdot: int


class User(UserBase):
    id: int

    class Config:
        orm_mode = True