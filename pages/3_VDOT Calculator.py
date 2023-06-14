import streamlit as st

import pandas as pd

from src.vdot import user_VDOT
from src.utils import num_time_to_str_time

DISTANCES = {
    "Marathon": 42.195,
    "Half Marathon": 21.097,
    "10km": 10.000,
    "5km": 5.000,
    "Custom": 0.,
}


def get_pace(dist, time):
    try:
        pace = time / dist
    except ZeroDivisionError:
        pace = 0
    pace_min, pace_sec = pace // 60, pace % 60
    return pace_min, pace_sec

system = st.sidebar.radio("Unit System", ('Metric', 'Imperial'), index=0)

dist_unit = 'kilometers'
if system is not None:
    st.session_state['system'] = system
    if st.session_state['system'] == 'Imperial':
        dist_unit = 'miles'

st.header('VDOT Calculator')

input_method = st.radio('Choose Inputs', ('Distance & Time', 'Distance & Pace', 'Time & Pace'), horizontal=True)
pace_disabled = input_method == 'Distance & Time'
time_disabled = input_method == 'Distance & Pace'
distance_disabled = input_method == 'Time & Pace'


st.subheader('Distance')
distance_selection_col, distance_input_col = st.columns(2)
default_distance = distance_selection_col.selectbox("Select distance", list(DISTANCES.keys()), key="pace_tab_distance_col_default_distance", disabled=distance_disabled)
distance = DISTANCES[default_distance]

if st.session_state['system'] == 'Imperial':
    distance /= 1.609

raw_distance = distance_input_col.number_input("Write your distance here", 0.0, value=distance, key="pace_tab_distance_col_distance", disabled=distance_disabled)

st.subheader('Time')

pace_tab_time_col1, pace_tab_time_col2, pace_tab_time_col3 = st.columns(3)
h = pace_tab_time_col1.number_input("Hours", value=0, min_value=0, key="pace_tab_time_col_hours", disabled=time_disabled)
m = pace_tab_time_col2.number_input("Minutes", value=0, min_value=0, max_value=59, key="pace_tab_time_col_minutes", disabled=time_disabled)
s = pace_tab_time_col3.number_input("Seconds", value=0, min_value=0, max_value=59, key="pace_tab_time_col_seconds", disabled=time_disabled)
time = h * 60 + m + s / 60

st.subheader('Pace')
distance_tab_pace_col1, distance_tab_pace_col2 = st.columns(2)
pace_min = distance_tab_pace_col1.number_input("Minutes", value=0, min_value=0, max_value=59, key="distance_tab_pace_col_minutes", disabled=pace_disabled)
pace_sec = distance_tab_pace_col2.number_input("Seconds", value=0, min_value=0, max_value=59, key="distance_tab_pace_col_seconds", disabled=pace_disabled)

if input_method == 'Distance & Time':
    pace_min, pace_sec = get_pace(raw_distance, time)
elif input_method == 'Distance & Pace':
    time = raw_distance * (pace_min + pace_sec / 60)
elif input_method == 'Time & Pace':
    raw_distance = time / (pace_min + pace_sec / 60)

try:
    vdot = user_VDOT(raw_distance, dist_unit, time)
except ZeroDivisionError:
    vdot = 0

st.title(f"VDOT: {vdot:.2f}")
# print(raw_distance, time, pace_min, pace_sec)

equivalent_tab, training_tab = st.tabs(['Equivalent Times', 'Training Paces'])

with equivalent_tab:
    df = pd.read_csv('data/interim/vdot-to-race-paces-coefficients.csv')

    df['Time'] = df.Coef1 * vdot + df.Coef2 * vdot ** 2 + df.Coef3 * vdot ** 3 + df.Coef4 * vdot ** 4 + df.Intercept

    df.Time = df.Time.apply(num_time_to_str_time)

    df = df.set_index('Distance')

    st.dataframe(df[['Time']].T)

with training_tab:
    df = pd.read_csv('data/interim/vdot-to-training-paces-coefficients.csv')

    df['Pace'] = df.Coef1 * vdot + df.Coef2 * vdot ** 2 + df.Coef3 * vdot ** 3 + df.Coef4 * vdot ** 4 + df.Intercept

    if st.session_state['system'] == 'Imperial':
        df['Pace'] *= 1.609

    df.Pace = df.Pace.apply(num_time_to_str_time)

    df = df.set_index('Distance')

    st.dataframe(df[['Pace']].T)

