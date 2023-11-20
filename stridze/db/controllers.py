from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from stridze.db.models import Activity, Lap, Record, User


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


def create_user(db: Session, user):
    db_user = User(**user.__dict__)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_activity(db: Session, activity) -> Activity:
    db_element = Activity(**activity.__dict__)
    # existing_element = db.query(Activity).filter(Activity.id == db_element.id).first()

    # if existing_element:
    #     for key, value in activity.__dict__.items():
    #         setattr(existing_element, key, value)
    #     return existing_element

    db.add(db_element)
    return db_element


def create_record(db: Session, record) -> Record:
    db_element = Record(**record.__dict__)
    # existing_element = (
    #     db.query(Record).filter(Record.timestamp == db_element.timestamp).first()
    # )

    # if existing_element:
    #     for key, value in record.__dict__.items():
    #         setattr(existing_element, key, value)
    #     return existing_element

    db.add(db_element)
    return db_element


def create_lap(db: Session, lap) -> Lap:
    db_element = Lap(**lap.__dict__)
    # existing_element = (
    #     db.query(Lap).filter(Lap.start_time == db_element.start_time).first()
    # )

    # if existing_element:
    #     for key, value in lap.__dict__.items():
    #         setattr(existing_element, key, value)
    #     return existing_element

    db.add(db_element)
    return db_element
