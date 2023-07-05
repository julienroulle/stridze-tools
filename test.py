from datetime import datetime
import os
import pandas as pd
import numpy as np
from sqlalchemy import text
import sqlalchemy
from db import get_session

from db.controllers import create_activity, create_user, get_user, get_db_size
from db.models import GPXPoint, Lap, Record, TCXLap, TrackPoint
from db.schemas.activity import ActivityBase
from db.schemas.user import UserBase

from functools import reduce

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

session = get_session()

# print(get_db_size(db=session))
# exit(1)

if False:
    sql = text('DROP TABLE IF EXISTS track_points;')
    result = session.execute(sql)
    sql = text('DROP TABLE IF EXISTS tcx_laps;')
    result = session.execute(sql)
    # sql = text('DROP TABLE IF EXISTS gpx_tracks;')
    # result = session.execute(sql)
    # sql = text('DROP TABLE IF EXISTS users;')
    # result = session.execute(sql)
    exit(1) 

user = UserBase(first_name="Julien", last_name="Roullé", email="ju.roulle@gmail.com", password="Julien35830", vdot=50)
# create_user(db=session, user=user)
user = get_user(session, "ju.roulle@gmail.com")
print(user.id)
# get_user(db, 1)

# import gpxpy

# for activity_id in os.listdir('data/raw/'):
#     if activity_id.endswith('.DS_Store'):
#         continue

#     df = pd.read_csv(f"data/raw/{activity_id}/{activity_id}.csv")
#     df = df.replace('--', None)
#     result = df.loc[df.Intervalle == 'Summary'].iloc[0]

#     try:
#         activity = ActivityBase(
#             id = int(activity_id),
#             user_id = user.id,
#             elapsed_time = int(reduce(lambda acc, x: acc * 60 + float(x), result["Heure"].split(":"), 0)) if result["Heure"] else None,
#             moving_time = int(reduce(lambda acc, x: acc * 60 + float(x), result['Temps de déplacement'].split(":"), 0)) if result["Temps de déplacement"] else None,
#             distance = int(result[['Distance']].astype(float).iloc[0]) * 1000,
#             elevation_gain = int(result["Gain d'altitude"]) if result["Gain d'altitude"] else None,
#             elevation_loss = int(result["Perte d'altitude"]) if result["Perte d'altitude"] else None,
#             average_pace = int(reduce(lambda acc, x: acc * 60 + float(x), result['Allure moyenne'].split(":"), 0)) if result["Allure moyenne"] else None,
#             average_moving_pace = int(reduce(lambda acc, x: acc * 60 + float(x), result['Allure moyenne en déplacement'].split(":"), 0)) if result["Allure moyenne en déplacement"] else None,
#             average_cadence = int(result['Cadence de course moyenne']) if result["Cadence de course moyenne"] else None,
#             average_heart_rate = int(result['Fréquence cardiaque moy.']) if result["Fréquence cardiaque moy."] else None,
#             max_heart_rate = int(result['Fréquence cardiaque maximale']) if result["Fréquence cardiaque maximale"] else None,
#             average_stride_length = float(result['Longueur moyenne des foulées']) if result["Longueur moyenne des foulées"] else None,
#             average_temperature = float(result['Température moyenne']) if result["Température moyenne"] else None,
#             calories = int(result['Calories']) if result["Calories"] else None,
#         )
#         create_activity(session, activity)

#         with open(f"data/raw/{activity_id}/{activity_id}.gpx", 'r') as gpx_file:
#             gpx_data = gpxpy.parse(gpx_file)

#             track = gpx_data.tracks[0]
#             gpx_points = track.segments[0].points

#             for point in gpx_points:
#                 gpx_point = GPXPoint(latitude=point.latitude, longitude=point.longitude, elevation=point.elevation, activity_id=activity_id)
#                 # Add and commit the object
#                 session.add(gpx_point)
#                 session.commit()

#     except sqlalchemy.exc.IntegrityError:
#         session.rollback()
        
#     except Exception as e:
#         print(activity_id)
#         print(e)
#         session.rollback()

# import fitdecode

# for activity_id in os.listdir('data/raw/'):
#     if activity_id.endswith('.DS_Store'):
#         continue
#     records = pd.DataFrame()
#     laps = pd.DataFrame()
#     with fitdecode.FitReader(f"data/raw/{activity_id}/{activity_id}_ACTIVITY.fit") as fit_file:
#         for frame in fit_file:
#             if frame.frame_type == fitdecode.FIT_FRAME_DATA:
#                 try:
#                     if frame.name == 'record':
#                         record = {'activity_id': activity_id}
#                         for elt in ['timestamp', 'position_lat', 'position_long', 'distance', 'altitude', 'enhanced_altitude', 'speed', 'enhanced_speed', 'heart_rate', 'cadence']:
#                             record[elt] = frame.get_value(elt, fallback=None)
#                         record = Record(**record)
#                         session.add(record)
#                         session.commit()
#                         # records = pd.concat([records, pd.DataFrame(record, index=[0])])
#                     if frame.name == 'lap':
#                         lap = {'activity_id': activity_id}
#                         for elt in ['start_time', 'start_position_lat', 'start_position_long', 'total_elapsed_time', 'total_distance', 'total_calories', 'avg_speed', 'max_speed', 'total_ascent', 'total_descent', 'avg_heart_rate', 'max_heart_rate', 'avg_cadence', 'max_cadence', 'avg_power', 'max_power']:
#                             lap[elt] = frame.get_value(elt, fallback=None)
#                         lap = Lap(**lap)
#                         session.add(lap)
#                         session.commit()
#                     # laps = pd.concat([laps, pd.DataFrame(lap, index=[0])])
                
#                 except sqlalchemy.exc.IntegrityError:
#                     session.rollback()

from lxml import objectify

for activity_id in os.listdir('data/raw/'):
    if activity_id.endswith('.DS_Store'):
        continue

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
            total_time_seconds=get_numeric_value(lap_data.findall('.//ns:TotalTimeSeconds', namespaces={"ns": namespace}), float),
            distance_meters=get_numeric_value(lap_data.findall('.//ns:DistanceMeters', namespaces={"ns": namespace}), float),
            maximum_speed=get_numeric_value(lap_data.findall('.//ns:MaximumSpeed', namespaces={"ns": namespace}), float),
            start_time=datetime.strptime(lap_data.attrib["StartTime"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S'),
            calories=get_numeric_value(lap_data.findall('.//ns:Calories', namespaces={"ns": namespace}), float),
            intensity=str(lap_data.findall('.//ns:Intensity', namespaces={"ns": namespace})[0]),
            triggered_method=str(lap_data.findall('.//ns:TriggerMethod', namespaces={"ns": namespace})[0]),
            average_bpm=get_numeric_value(lap_data.findall('.//ns:AverageHeartRateBpm/ns:Value', namespaces={"ns": namespace}), int),
            maximum_bpm=get_numeric_value(lap_data.findall('.//ns:MaximumHeartRateBpm/ns:Value', namespaces={"ns": namespace}), int),
        )
        print(lap)
        lap = TCXLap(**lap)
        session.add(lap)
        session.commit()
        for track_data in lap_data.findall(".//ns:Track/ns:Trackpoint", namespaces={"ns": namespace}):
            trackpoint = dict(
                lap_id=int(lap.id),
                time=datetime.strptime(track_data.findall('.//ns:Time', namespaces={"ns": namespace})[0].text, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S'),
                altitude=get_numeric_value(track_data.findall('.//ns:AltitudeMeters', namespaces={"ns": namespace}), float),
                distance=get_numeric_value(track_data.findall('.//ns:DistanceMeters', namespaces={"ns": namespace}), float),
                latitude=get_numeric_value(track_data.findall('.//ns:Position/ns:LatitudeDegrees', namespaces={"ns": namespace}), float),
                longitude=get_numeric_value(track_data.findall('.//ns:Position/ns:LongitudeDegrees', namespaces={"ns": namespace}), float),
                heart_rate=get_numeric_value(track_data.findall('.//ns:HeartRateBpm/ns:Value', namespaces={"ns": namespace}), int)
            )

            for extension in track_data.findall('.//ns:Extensions', namespaces={"ns": namespace}):
                for elt in extension.findall('.//ns:TPX', namespaces={"ns": ext_namespace}):
                    trackpoint['speed'] = get_numeric_value(elt.findall('.//ns:Speed', namespaces={"ns": ext_namespace}), float)
                    trackpoint['cadence'] = get_numeric_value(elt.findall('.//ns:RunCadence', namespaces={"ns": ext_namespace}), int)
            trackpoint = TrackPoint(**trackpoint)
            session.add(trackpoint)
            session.commit()