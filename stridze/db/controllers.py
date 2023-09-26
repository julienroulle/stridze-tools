from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from .models.activity import Activity
from .models.user import User
from .schemas.activity import ActivityBase
from .schemas.user import UserBase


def get_db_size(db: Session) -> None:
    query = "SELECT pg_size_pretty(pg_database_size(current_database())) AS size;"
    result = db.execute(query)

    # Fetch the result
    size = result.fetchone()[0]

    # Print the size of the database
    print(f"The size of the database is: {size}")


def clear_all_tables(db: Session):
    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    for table in reversed(metadata.sorted_tables):
        table.drop(db.bind)

    db.commit()


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
