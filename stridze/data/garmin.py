import io
import zipfile

import fitdecode
from garminconnect import Garmin
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from stridze.db import engine
from stridze.db.models import Activity, Lap, Record


def main():
    session = sessionmaker(engine)()
    SQLModel.metadata.create_all(engine)
    client = Garmin("ju.roulle@gmail.com", "Julien35830")
    client.login()
    activities = client.get_activities(0, 10)
    """
    Download an Activity
    """
    for activity in activities:
        activity_id = activity["activityId"]
        query = select(Activity).where(Activity.garmin_id == activity_id)
        result = session.execute(query).first()
        if result:
            continue
        data = client.download_activity(
            activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL
        )
        print(f"Downloaded activity {activity_id}")
        activity = Activity(
            garmin_id=activity_id,
            activity_type=activity["activityType"]["typeKey"],
            start_time=activity["startTimeLocal"],
            start_position_lat=activity["startLatitude"],
            start_position_long=activity["startLongitude"],
            distance=activity["distance"],
            duration=activity["duration"],
            elapsed_time=activity["elapsedDuration"],
            moving_time=activity["movingDuration"],
            elevation_gain=activity["elevationGain"],
            elevation_loss=activity["elevationLoss"],
            average_speed=activity["averageSpeed"],
            max_speed=activity["maxSpeed"],
            average_heart_rate=activity["averageHR"],
            max_heart_rate=activity["maxHR"],
            calories=activity["calories"],
        )
        session.add(activity)
        with zipfile.ZipFile(io.BytesIO(data), "r") as zip_file:
            for file_name in zip_file.namelist():
                file_content = zip_file.read(file_name)

                # Extract all files in the zip archive into the memory file
                memory_file = io.BytesIO()

                # Read the contents of the extracted file into an io.BytesIO buffer
                memory_file.write(file_content)

                # Reset the memory file's position to the beginning
                memory_file.seek(0)
                with fitdecode.FitReader(memory_file) as fit_file:
                    records = []
                    for frame in fit_file:
                        if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                            if frame.name == "record":
                                record = {}
                                for field in frame.fields:
                                    if "unknown" not in field.name:
                                        record[field.name] = field.value
                                records.append(record)
                            elif frame.name == "lap":
                                lap = {}
                                for field in frame.fields:
                                    if "unknown" not in field.name:
                                        lap[field.name] = field.value
                                lap = Lap(**lap, activity=activity)
                                session.add(lap)
                                for record in records:
                                    record = Record(
                                        **record, activity=activity, lap=lap
                                    )
                                    session.add(record)
                                records = []
                                session.commit()


if __name__ == "__main__":
    main()
