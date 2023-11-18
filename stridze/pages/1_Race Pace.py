import streamlit as st

DISTANCES = {
    "Marathon": 42.195,
    "Half Marathon": 21.097,
    "10km": 10.000,
    "5km": 5.000,
    "Custom": 0.0,
}


def get_pace(dist, time):
    try:
        pace = time / dist
    except ZeroDivisionError:
        pace = 0
    pace_min, pace_sec = pace // 60, pace % 60
    return pace_min, pace_sec


st.title("Race Calculator")

system = st.sidebar.radio("Unit System", ("Metric", "Imperial"), index=0)
if system is not None:
    st.session_state["system"] = system

pace_tab, distance_tab, time_tab = st.tabs(["Pace", "Distance", "Time"])

with pace_tab:
    dist_unit = "km"
    if st.session_state["system"] == "Imperial":
        dist_unit = "mi"
    pace_tab_distance_col, _, pace_tab_time_col = st.columns([8, 0.5, 10])

    pace_tab_distance_col.subheader(f"Distance ({dist_unit})")

    default_distance = pace_tab_distance_col.selectbox(
        "Select distance",
        list(DISTANCES.keys()),
        key="pace_tab_distance_col_default_distance",
    )
    distance = DISTANCES[default_distance]

    if st.session_state["system"] == "Imperial":
        distance /= 1.609

    raw_distance = pace_tab_distance_col.number_input(
        "Write your distance here",
        0.0,
        value=distance,
        key="pace_tab_distance_col_distance",
    )

    pace_tab_time_col.subheader("Time")
    (
        pace_tab_time_col1,
        pace_tab_time_col2,
        pace_tab_time_col3,
    ) = pace_tab_time_col.columns(3)
    h = pace_tab_time_col1.number_input(
        "Hours", value=0, min_value=0, key="pace_tab_time_col_hours"
    )
    m = pace_tab_time_col2.number_input(
        "Minutes", value=0, min_value=0, max_value=59, key="pace_tab_time_col_minutes"
    )
    s = pace_tab_time_col3.number_input(
        "Seconds", value=0, min_value=0, max_value=59, key="pace_tab_time_col_seconds"
    )
    time = h * 3600 + m * 60 + s
    pace_min, pace_sec = get_pace(raw_distance, time)
    st.header(f"Average pace: {pace_min:.0f}:{pace_sec:02.0f}s/{dist_unit}")


with distance_tab:
    dist_unit = "km"
    if st.session_state["system"] == "Imperial":
        dist_unit = "mi"

    distance_tab_time_col, _, distance_tab_pace_col = st.columns([10, 0.5, 8])

    distance_tab_time_col.subheader("Time")
    (
        distance_tab_time_col1,
        distance_tab_time_col2,
        distance_tab_time_col3,
    ) = distance_tab_time_col.columns(3)
    h = distance_tab_time_col1.number_input(
        "Hours", value=0, min_value=0, key="distance_tab_time_col_hours"
    )
    m = distance_tab_time_col2.number_input(
        "Minutes",
        value=0,
        min_value=0,
        max_value=59,
        key="distance_tab_time_col_minutes",
    )
    s = distance_tab_time_col3.number_input(
        "Seconds",
        value=0,
        min_value=0,
        max_value=59,
        key="distance_tab_time_col_seconds",
    )
    time = h * 3600 + m * 60 + s

    distance_tab_pace_col.subheader(f"Pace (min/{dist_unit})")

    distance_tab_pace_col1, distance_tab_pace_col2 = distance_tab_pace_col.columns(2)
    pace_min = distance_tab_pace_col1.number_input(
        "Minutes",
        value=0,
        min_value=0,
        max_value=59,
        key="distance_tab_pace_col_minutes",
    )
    pace_sec = distance_tab_pace_col2.number_input(
        "Seconds",
        value=0,
        min_value=0,
        max_value=59,
        key="distance_tab_pace_col_seconds",
    )
    pace = pace_min * 60 + pace_sec

    try:
        distance = time / pace
    except ZeroDivisionError:
        distance = 0.0

    st.header(f"Distance: {distance:.2f} {dist_unit}")


with time_tab:
    dist_unit = "km"
    if st.session_state["system"] == "Imperial":
        dist_unit = "mi"

    time_tab_pace_col, _, time_tab_distance_col = st.columns([8, 0.5, 8])

    time_tab_pace_col.subheader(f"Pace (min/{dist_unit})")

    column1, column2 = time_tab_pace_col.columns(2)
    pace_min = column1.number_input("Minutes", 0)
    pace_sec = column2.number_input("Seconds", 0)
    pace = pace_min * 60 + pace_sec

    time_tab_distance_col.subheader(f"Distance ({dist_unit})")

    default_distance = time_tab_distance_col.selectbox(
        "Select distance", list(DISTANCES.keys())
    )
    distance = DISTANCES[default_distance]

    if st.session_state["system"] == "Imperial":
        distance /= 1.609

    raw_distance = time_tab_distance_col.number_input(
        "Write your distance here", 0.0, value=distance
    )

    time = raw_distance * pace
    h = time // 3600
    m = (time - h * 3600) // 60
    s = time % 60
    st.header(f"Time: {h:.0f}:{m:02.0f}:{s:02.0f}")

st.markdown("""---""")
