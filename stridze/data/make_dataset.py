import datetime
import os
from contextlib import contextmanager
from functools import reduce

import fitdecode
import gpxpy
import pandas as pd
import sqlalchemy
from garminconnect import Garmin
from lxml import objectify

from stridze.db import get_session
from stridze.db.controllers import (
    clear_all_tables,
    create_activity,
    create_lap,
    create_record,
    create_user,
    get_user,
)
from stridze.db.models import GPXPoint, Lap, Record, TCXLap, TrackPoint
from stridze.db.models.activity import Activity
from stridze.db.schemas.activity import ActivityBase
from stridze.db.schemas.lap import LapBase
from stridze.db.schemas.record import RecordBase
from stridze.db.schemas.user import UserBase


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
                        "enhanced_speed",
                        "enhanced_altitude",
                        "vertical_oscillation",
                        "stance_time_percent",
                        "stance_time",
                        "vertical_ratio",
                        "stance_time_balance",
                        "step_length",
                        "heart_rate",
                        "cadence",
                    ]:
                        record[elt] = frame.get_value(elt, fallback=None)
                        if (
                            elt in ["position_lat", "position_long"]
                            and record[elt] is not None
                        ):
                            record[elt] /= 2**32 / 360
                    create_record(session, RecordBase(**record))

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
                    create_lap(session, LapBase(**lap))

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
        # clear_all_tables(session)
        # exit(1)
        # create_user(db=session, user=user)
        user = get_user(session, "ju.roulle@gmail.com")
        print(user.id)

        client = Garmin(user.email, user.password)
        client.login()
        # get_user(db, 1)
        for activity_id in os.listdir("data/raw/"):
            if activity_id.endswith(".DS_Store"):
                continue

            print(f"Processing activity {activity_id}")
            print(client.get_activity_details(activity_id).keys())
            if session.query(Activity).filter(Activity.id == activity_id).first():
                # print(f"Activity {activity_id} already processed")
                continue

            df = pd.read_csv(f"data/raw/{activity_id}/{activity_id}.csv")
            df = df.replace("--", None)
            result = df.loc[df.Intervalle == "Summary"].iloc[0]

            if "Allure moyenne" in result:
                average_pace = int(
                    reduce(
                        lambda acc, x: acc * 60 + float(x),
                        result["Allure moyenne"].split(":"),
                        0,
                    )
                )
                average_moving_pace = int(
                    reduce(
                        lambda acc, x: acc * 60 + float(x),
                        result["Allure moyenne en déplacement"].split(":"),
                        0,
                    )
                )
            elif "Vitesse moyenne" in result:
                average_pace = int(result["Vitesse moyenne"])
                average_moving_pace = int(result["Vitesse moyenne en déplacement"])

            try:
                activity = ActivityBase(
                    id=int(activity_id),
                    user_id=user.id,
                    elapsed_time=int(
                        reduce(
                            lambda acc, x: acc * 60 + float(x),
                            result["Heure"].split(":"),
                            0,
                        )
                    )
                    if "Heure" in result
                    else None,
                    moving_time=int(
                        reduce(
                            lambda acc, x: acc * 60 + float(x),
                            result["Temps de déplacement"].split(":"),
                            0,
                        )
                    )
                    if "Temps de déplacement" in result
                    else None,
                    distance=int(result[["Distance"]].astype(float).iloc[0] * 1000),
                    elevation_gain=int(result["Gain d'altitude"])
                    if "Gain d'altitude" in result
                    else None,
                    elevation_loss=int(result["Perte d'altitude"])
                    if "Perte d'altitude" in result
                    else None,
                    average_pace=average_pace,
                    average_moving_pace=average_moving_pace,
                    average_cadence=int(result["Cadence de course moyenne"])
                    if "Cadence de course moyenne" in result
                    else None,
                    average_heart_rate=int(result["Fréquence cardiaque moy."])
                    if "Fréquence cardiaque moy." in result
                    else None,
                    max_heart_rate=int(result["Fréquence cardiaque maximale"])
                    if "Fréquence cardiaque maximale" in result
                    else None,
                    average_stride_length=float(result["Longueur moyenne des foulées"])
                    if "Longueur moyenne des foulées" in result
                    else None,
                    average_temperature=float(result["Température moyenne"])
                    if "Température moyenne" in result
                    else None,
                    calories=int(result["Calories"]) if "Calories" in result else None,
                )
                create_activity(session, activity)

            except sqlalchemy.exc.IntegrityError as ex:
                print("IntegrityError")
                print(ex.orig)
                print(ex.statement)
                session.rollback()

            except Exception as e:
                print(e)
                session.rollback()
                continue

            # process_gpx_files(activity_id, session)
            process_fit_files(activity_id, session)
            # process_tcx_files(activity_id, session)


if __name__ == "__main__":
    main()
