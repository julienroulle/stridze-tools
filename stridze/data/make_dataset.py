import datetime
import os
from contextlib import contextmanager
from functools import reduce

import fitdecode
import gpxpy
import pandas as pd
import sqlalchemy
from db import get_session
from db.controllers import create_activity, create_user, get_db_size, get_user
from db.models import GPXPoint, Lap, Record, TCXLap, TrackPoint
from db.schemas.activity import ActivityBase
from db.schemas.user import UserBase
from lxml import objectify


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_numeric_value(elements, data_type):
    try:
        value = float(elements[0])
        if data_type == int:
            return int(value)
        elif data_type == float:
            return value
        else:
            raise ValueError("Invalid data type specified")
    except (IndexError, ValueError):
        return None


def calculate_pace(time_seconds, distance_meters):
    # Convert distance to kilometers
    distance_km = distance_meters / 1000

    # Convert time to minutes
    time_minutes = time_seconds / 60

    # Calculate pace
    pace = time_minutes / distance_km

    return pace


def process_gpx_files(activity_id, session):
    with open(f"data/raw/{activity_id}/{activity_id}.gpx", "r") as gpx_file:
        gpx_data = gpxpy.parse(gpx_file)

        track = gpx_data.tracks[0]
        gpx_points = track.segments[0].points

        for point in gpx_points:
            gpx_point = GPXPoint(
                latitude=point.latitude,
                longitude=point.longitude,
                elevation=point.elevation,
                activity_id=activity_id,
            )
            session.add(gpx_point)
        session.commit()


def process_fit_files(activity_id, session):
    with fitdecode.FitReader(
        f"data/raw/{activity_id}/{activity_id}_ACTIVITY.fit"
    ) as fit_file:
        for frame in fit_file:
            if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                if frame.name == "record":
                    record = {"activity_id": activity_id}
                    for elt in [
                        "timestamp",
                        "position_lat",
                        "position_long",
                        "distance",
                        "altitude",
                        "enhanced_altitude",
                        "speed",
                        "enhanced_speed",
                        "heart_rate",
                        "cadence",
                    ]:
                        record[elt] = frame.get_value(elt, fallback=None)
                        if (
                            elt in ["position_lat", "position_long"]
                            and record[elt] is not None
                        ):
                            record[elt] /= 2**32 / 360
                    record = Record(**record)
                    session.add(record)
                if frame.name == "lap":
                    lap = {"activity_id": activity_id}
                    for elt in [
                        "start_time",
                        "start_position_lat",
                        "start_position_long",
                        "total_elapsed_time",
                        "total_distance",
                        "total_calories",
                        "avg_speed",
                        "max_speed",
                        "total_ascent",
                        "total_descent",
                        "avg_heart_rate",
                        "max_heart_rate",
                        "avg_cadence",
                        "max_cadence",
                        "avg_power",
                        "max_power",
                    ]:
                        lap[elt] = frame.get_value(elt, fallback=None)
                        if (
                            elt in ["start_position_lat", "start_position_long"]
                            and lap[elt] is not None
                        ):
                            lap[elt] /= 2**32 / 360
                    lap = Lap(**lap)
                    session.add(lap)
        session.commit()


def process_tcx_files(activity_id, session):
    activity = f"data/raw/{activity_id}/{activity_id}.tcx"
    # Parse the TCX file using ElementTree
    tree = objectify.parse(activity)
    root = tree.getroot()

    namespace = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    ext_namespace = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

    # Extract and save TCX data to the database
    activity = root.Activities.Activity

    for lap_data in root.findall(".//ns:Lap", namespaces={"ns": namespace}):
        lap = dict(
            activity_id=int(activity_id),
            total_time_seconds=get_numeric_value(
                lap_data.findall(
                    ".//ns:TotalTimeSeconds", namespaces={"ns": namespace}
                ),
                float,
            ),
            distance_meters=get_numeric_value(
                lap_data.findall(".//ns:DistanceMeters", namespaces={"ns": namespace}),
                float,
            ),
            maximum_speed=get_numeric_value(
                lap_data.findall(".//ns:MaximumSpeed", namespaces={"ns": namespace}),
                float,
            ),
            start_time=datetime.strptime(
                lap_data.attrib["StartTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%Y-%m-%d %H:%M:%S"),
            calories=get_numeric_value(
                lap_data.findall(".//ns:Calories", namespaces={"ns": namespace}), float
            ),
            average_bpm=get_numeric_value(
                lap_data.findall(
                    ".//ns:AverageHeartRateBpm/ns:Value", namespaces={"ns": namespace}
                ),
                int,
            ),
            maximum_bpm=get_numeric_value(
                lap_data.findall(
                    ".//ns:MaximumHeartRateBpm/ns:Value", namespaces={"ns": namespace}
                ),
                int,
            ),
        )
        lap = TCXLap(**lap)
        session.add(lap)
    session.commit()
    for track_data in lap_data.findall(
        ".//ns:Track/ns:Trackpoint", namespaces={"ns": namespace}
    ):
        trackpoint = dict(
            lap_id=int(lap.id),
            time=datetime.strptime(
                track_data.findall(".//ns:Time", namespaces={"ns": namespace})[0].text,
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ).strftime("%Y-%m-%d %H:%M:%S"),
            altitude=get_numeric_value(
                track_data.findall(
                    ".//ns:AltitudeMeters", namespaces={"ns": namespace}
                ),
                float,
            ),
            distance=get_numeric_value(
                track_data.findall(
                    ".//ns:DistanceMeters", namespaces={"ns": namespace}
                ),
                float,
            ),
            latitude=get_numeric_value(
                track_data.findall(
                    ".//ns:Position/ns:LatitudeDegrees",
                    namespaces={"ns": namespace},
                ),
                float,
            ),
            longitude=get_numeric_value(
                track_data.findall(
                    ".//ns:Position/ns:LongitudeDegrees",
                    namespaces={"ns": namespace},
                ),
                float,
            ),
            heart_rate=get_numeric_value(
                track_data.findall(
                    ".//ns:HeartRateBpm/ns:Value", namespaces={"ns": namespace}
                ),
                int,
            ),
        )

        for extension in track_data.findall(
            ".//ns:Extensions", namespaces={"ns": namespace}
        ):
            for elt in extension.findall(".//ns:TPX", namespaces={"ns": ext_namespace}):
                trackpoint["speed"] = get_numeric_value(
                    elt.findall(".//ns:Speed", namespaces={"ns": ext_namespace}),
                    float,
                )
                trackpoint["cadence"] = get_numeric_value(
                    elt.findall(".//ns:RunCadence", namespaces={"ns": ext_namespace}),
                    int,
                )
        trackpoint = TrackPoint(**trackpoint)
        session.add(trackpoint)
    session.commit()


def main():
    user = UserBase(
        first_name="Julien",
        last_name="Roullé",
        email="ju.roulle@gmail.com",
        password="Julien35830",
    )
    with session_scope() as session:
        # create_user(db=session, user=user)
        user = get_user(session, "ju.roulle@gmail.com")
        print(user.id)
        # get_user(db, 1)

    for activity_id in os.listdir("data/raw/"):
        if activity_id.endswith(".DS_Store"):
            continue

        with session_scope() as session:
            # process_gpx_files(activity_id, session)
            process_fit_files(activity_id, session)
            # process_tcx_files(activity_id, session)


if __name__ == "__main__":
    main()
