import pathlib

import streamlit as st
from xgboost import XGBRegressor

system = st.sidebar.radio("Unit System", ("Metric", "Imperial"), index=0)

dist_unit = "kilometers"
if system is not None:
    st.session_state["system"] = system
    if st.session_state["system"] == "Imperial":
        dist_unit = "miles"

st.title("Treadmill Pace Calculator")

model = XGBRegressor()
path = pathlib.Path(__file__).parent.parent.absolute()
model_path = path.joinpath("models/treadmill_incline.json")

model.load_model(model_path)

grade_header, grade_clm = st.columns([1, 2])

grade_header.header("Incline (%)")
grade = grade_clm.slider("", 0, 15, 0, 1)

pace_header, pace_min_clm, pace_sec_clm = st.columns(3)
pace_header.header("Pace (min/km)")
pace_min = pace_min_clm.number_input(
    "Minutes",
    value=0,
    min_value=0,
    max_value=59,
    key="distance_tab_pace_col_minutes",
)
pace_sec = pace_sec_clm.number_input(
    "Seconds",
    value=0,
    min_value=0,
    max_value=59,
    key="distance_tab_pace_col_seconds",
)

pace = pace_min + pace_sec / 60

treadmill_speed = model.predict([[grade, pace]])[0]

speed_header, speed_value = st.columns(2)
speed_header.header("Target Speed: ")
speed_value.header(f"{60 / pace:.2f} km/h")
speed_header, speed_value = st.columns(2)
speed_header.header("Treadmill Speed: ")
speed_value.header(f"{treadmill_speed:.2f} km/h")
