from datetime import datetime
from typing import List, Optional

from sqlmodel import BigInteger, Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True, index=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    email: str = Field(unique=True, index=True)
    password: Optional[str] = Field(default=None)

    activities: List["Activity"] = Relationship(back_populates="user")

    def __str__(self):
        return f"User ({self.id})"


class Activity(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True, index=True)
    garmin_id: Optional[int] = Field(sa_column=Column(BigInteger()))
    activity_type: Optional[str]
    start_time: Optional[datetime]
    start_position_lat: Optional[float]
    start_position_long: Optional[float]
    distance: Optional[float]
    duration: Optional[float]
    elapsed_time: Optional[float]
    moving_time: Optional[float]
    elevation_gain: Optional[float]
    elevation_loss: Optional[float]
    average_speed: Optional[float]
    max_speed: Optional[float]
    average_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    calories: Optional[int]

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="activities")

    laps: List["Lap"] = Relationship(back_populates="activity")
    records: List["Record"] = Relationship(back_populates="activity")


class Lap(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True, index=True)
    timestamp: Optional[datetime]
    start_time: Optional[datetime]
    start_position_lat: Optional[float]
    start_position_long: Optional[float]
    end_position_lat: Optional[float]
    end_position_long: Optional[float]
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

    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    activity: Optional[Activity] = Relationship(back_populates="laps")

    records: List["Record"] = Relationship(back_populates="lap")


class Record(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

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

    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    activity: Optional[Activity] = Relationship(back_populates="records")


class Strava(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True, index=True)
    timestamp: Optional[datetime]
    temperature: Optional[int]
    moving: Optional[bool]
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]
    grade: Optional[float]
    cadence: Optional[float]
    distance: Optional[float]
    heartrate: Optional[float]
    elevation: Optional[float]
    activity_id: Optional[int] = Field(sa_column=Column(BigInteger()))
    user_id: Optional[int] = Field(sa_column=Column(BigInteger()))


class StravaToken(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True, index=True)
    access_token: Optional[str]
    refresh_token: Optional[str]
    expires_at: Optional[int]
    scope: Optional[str]
    athlete: Optional[str]
