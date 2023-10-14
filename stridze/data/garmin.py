import io
import zipfile
from datetime import datetime
from typing import List, Optional

import fitdecode
from garminconnect import Garmin
from sqlalchemy.orm import sessionmaker
from sqlmodel import BigInteger, Column, Field, Relationship, SQLModel

from stridze.db import engine


class FitActivity(SQLModel, table=True, extend_existing=True):
    id: int = Field(default=None, primary_key=True, index=True)
    garmin_id: Optional[int] = Field(sa_column=Column(BigInteger()))

    laps: List["Lap"] = Relationship(back_populates="fitactivity")
    records: List["Record"] = Relationship(back_populates="fitactivity")


class Lap(SQLModel, table=True, extend_existing=True):
    id: int = Field(default=None, primary_key=True, index=True)
    timestamp: Optional[datetime]
    start_time: Optional[datetime]
    start_position_lat: Optional[int]
    start_position_long: Optional[int]
    end_position_lat: Optional[int]
    end_position_long: Optional[int]
    total_elapsed_time: Optional[float]
    total_timer_time: Optional[float]
    total_distance: Optional[float]
    total_strides: Optional[int]
    total_work: Optional[float]
    time_standing: Optional[float]
    avg_left_power_phase: Optional[str]
    avg_left_power_phase_peak: Optional[str]
    avg_right_power_phase: Optional[str]
    avg_right_power_phase_peak: Optional[str]
    avg_power_position: Optional[str]
    max_power_position: Optional[str]
    enhanced_avg_speed: Optional[float]
    enhanced_max_speed: Optional[float]
    enhanced_avg_altitude: Optional[float]
    enhanced_min_altitude: Optional[float]
    enhanced_max_altitude: Optional[float]
    total_grit: Optional[float]
    avg_flow: Optional[float]
    message_index: Optional[int]
    total_calories: Optional[int]
    total_fat_calories: Optional[float]
    avg_speed: Optional[float]
    max_speed: Optional[float]
    avg_power: Optional[float]
    max_power: Optional[float]
    total_ascent: Optional[int]
    total_descent: Optional[int]
    num_lengths: Optional[int]
    normalized_power: Optional[float]
    left_right_balance: Optional[float]
    first_length_index: Optional[int]
    avg_stroke_distance: Optional[float]
    num_active_lengths: Optional[int]
    wkt_step_index: Optional[int]
    avg_vertical_oscillation: Optional[float]
    avg_stance_time_percent: Optional[float]
    avg_stance_time: Optional[float]
    stand_count: Optional[int]
    avg_vertical_ratio: Optional[float]
    avg_stance_time_balance: Optional[float]
    avg_step_length: Optional[float]
    event: Optional[str]
    event_type: Optional[str]
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    avg_running_cadence: Optional[int]
    max_running_cadence: Optional[int]
    intensity: Optional[float]
    lap_trigger: Optional[str]
    sport: Optional[str]
    event_group: Optional[int]
    swim_stroke: Optional[str]
    sub_sport: Optional[str]
    avg_temperature: Optional[int]
    max_temperature: Optional[int]
    avg_fractional_cadence: Optional[float]
    max_fractional_cadence: Optional[float]
    total_fractional_cycles: Optional[float]
    avg_left_torque_effectiveness: Optional[float]
    avg_right_torque_effectiveness: Optional[float]
    avg_left_pedal_smoothness: Optional[float]
    avg_right_pedal_smoothness: Optional[float]
    avg_combined_pedal_smoothness: Optional[float]
    avg_left_pco: Optional[float]
    avg_right_pco: Optional[float]
    avg_cadence_position: Optional[str]
    max_cadence_position: Optional[str]
    total_fractional_ascent: Optional[float]
    total_fractional_descent: Optional[float]

    fitactivity_id: Optional[int] = Field(default=None, foreign_key="fitactivity.id")
    fitactivity: Optional[FitActivity] = Relationship(back_populates="laps")

    records: List["Record"] = Relationship(back_populates="lap")


class Record(SQLModel, table=True, extend_existing=True):
    id: int = Field(default=None, primary_key=True, index=True)
    timestamp: Optional[datetime]
    position_lat: Optional[int]
    position_long: Optional[int]
    distance: Optional[float]
    enhanced_speed: Optional[float]
    enhanced_altitude: Optional[float]
    vertical_oscillation: Optional[float]
    stance_time_percent: Optional[float]
    stance_time: Optional[float]
    vertical_ratio: Optional[float]
    stance_time_balance: Optional[float]
    step_length: Optional[float]
    heart_rate: Optional[int]
    cadence: Optional[int]
    temperature: Optional[int]
    activity_type: Optional[str]
    fractional_cadence: Optional[float]

    lap_id: Optional[int] = Field(default=None, foreign_key="lap.id")
    lap: Optional[Lap] = Relationship(back_populates="records")

    fitactivity_id: Optional[int] = Field(default=None, foreign_key="fitactivity.id")
    fitactivity: Optional[FitActivity] = Relationship(back_populates="records")


def main():
    session = sessionmaker(engine)()
    SQLModel.metadata.create_all(engine)
    client = Garmin("ju.roulle@gmail.com", "Julien35830")
    client.login()
    activities = client.get_activities(0, 100)
    """
    Download an Activity
    """
    for activity in activities:
        activity_id = activity["activityId"]
        data = client.download_activity(
            activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL
        )
        print(f"Downloaded activity {activity_id}")
        activity = FitActivity(garmin_id=activity_id)
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
                                lap = Lap(**lap, fitactivity=activity)
                                session.add(lap)
                                for record in records:
                                    record = Record(
                                        **record, fitactivity=activity, lap=lap
                                    )
                                    session.add(record)
                                records = []
                                session.commit()
        break


if __name__ == "__main__":
    main()
