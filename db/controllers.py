from sqlalchemy import text
from sqlalchemy.orm import Session
import typing as t

from .models.user import User
from .models.activity import Activity

from .schemas.user import UserBase
from .schemas.activity import ActivityBase

def get_db_size(db: Session) -> None:
    query = text("SELECT SUM(data_length + index_length) / 1024 / 1024 AS size_mb FROM information_schema.tables WHERE table_schema = DATABASE();")
    result = db.execute(query)
    size_mb = result.scalar()

    print(f"The size of the database is approximately {size_mb} MB.")

def get_user(db: Session, user_email: str) -> User:
    user = db.query(User).filter(User.email == user_email).first()
    # if not user: return
    return user

def create_user(db: Session, user: UserBase):
    db_user = User(**user.__dict__)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_activity(db: Session, activity: ActivityBase) -> Activity:
    db_element = Activity(**activity.__dict__)
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element