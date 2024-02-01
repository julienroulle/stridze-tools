import os
from datetime import datetime
from functools import reduce

import fitdecode
import gpxpy
import numpy as np
import pandas as pd
import sqlalchemy
from lxml import objectify
from sqlalchemy import text

from stridze.db import engine, get_session
from stridze.db.controllers import create_activity, create_user, get_db_size, get_user
from stridze.db.models import GPXPoint, Lap, Record, TCXLap, TrackPoint
from stridze.db.schemas.activity import ActivityBase
from stridze.db.schemas.user import UserBase

session = get_session()

user = UserBase(
    first_name="Julien",
    last_name="Roullé",
    email="ju.roulle@gmail.com",
    password="Julien35830",
    vdot=50,
)
create_user(db=session, user=user)
user = get_user(session, "ju.roulle@gmail.com")
print(user.id)
# get_user(db, 1)

for activity_id in os.listdir("data/raw/"):
    print(activity_id)
    if activity_id.endswith(".DS_Store"):
        continue

    df = pd.read_csv(f"data/raw/{activity_id}/{activity_id}.csv")
    df = df.replace("--", None)
    result = df.loc[df.Intervalle == "Summary"].iloc[0]

    try:
        activity = ActivityBase(
            id=int(activity_id),
            user_id=user.id,
            elapsed_time=int(
                reduce(
                    lambda acc, x: acc * 60 + float(x), result["Heure"].split(":"), 0
                )
            )
            if result["Heure"]
            else None,
            moving_time=int(
                reduce(
                    lambda acc, x: acc * 60 + float(x),
                    result["Temps de déplacement"].split(":"),
                    0,
                )
            )
            if result["Temps de déplacement"]
            else None,
            distance=int(result[["Distance"]].astype(float).iloc[0]) * 1000,
            elevation_gain=int(result["Gain d'altitude"])
            if result["Gain d'altitude"]
            else None,
            elevation_loss=int(result["Perte d'altitude"])
            if result["Perte d'altitude"]
            else None,
            average_pace=int(
                reduce(
                    lambda acc, x: acc * 60 + float(x),
                    result["Allure moyenne"].split(":"),
                    0,
                )
            )
            if result["Allure moyenne"]
            else None,
            average_moving_pace=int(
                reduce(
                    lambda acc, x: acc * 60 + float(x),
                    result["Allure moyenne en déplacement"].split(":"),
                    0,
                )
            )
            if result["Allure moyenne en déplacement"]
            else None,
            average_cadence=int(result["Cadence de course moyenne"])
            if result["Cadence de course moyenne"]
            else None,
            average_heart_rate=int(result["Fréquence cardiaque moy."])
            if result["Fréquence cardiaque moy."]
            else None,
            max_heart_rate=int(result["Fréquence cardiaque maximale"])
            if result["Fréquence cardiaque maximale"]
            else None,
            average_stride_length=float(result["Longueur moyenne des foulées"])
            if result["Longueur moyenne des foulées"]
            else None,
            average_temperature=float(result["Température moyenne"])
            if result["Température moyenne"]
            else None,
            calories=int(result["Calories"]) if result["Calories"] else None,
        )
        create_activity(session, activity)

    except sqlalchemy.exc.IntegrityError as ex:
        # print("IntegrityError")
        # print(ex.orig)
        # print(ex.statement)
        session.rollback()

    except Exception as e:
        print(e)
        session.rollback()
        continue

    records = pd.DataFrame()
    laps = pd.DataFrame()
    try:
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
                        # records = pd.concat([records, pd.DataFrame(record, index=[0])])
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
                    # laps = pd.concat([laps, pd.DataFrame(lap, index=[0])])
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        print("IntegrityError")
        session.rollback()
