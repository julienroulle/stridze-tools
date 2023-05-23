import streamlit as st

DISTANCES = {
    "5km": 5.000,
    "10km": 10.000,
    "Half Marathon": 21.097,
    "Marathon": 42.195,
    "Custom": None,
}


def get_pace(dist, time):
    pace = time / dist
    pace_min, pace_sec = pace // 60, pace % 60
    return pace_min, pace_sec

st.title('Race Calculator')

pace_tab, distance_tab, time_tab = st.tabs(['Pace', 'Distance', 'Time'])

with pace_tab:
    pace_tab_distance_col, _, pace_tab_time_col= st.columns([8, 0.5, 10])

    pace_tab_distance_col.subheader("Distance")

    default_distance = pace_tab_distance_col.selectbox("Select distance", list(DISTANCES.keys()), key="pace_tab_distance_col_default_distance")
    distance = DISTANCES[default_distance]
    pace_tab_distance_col1, pace_tab_distance_col2 = pace_tab_distance_col.columns([2, 1])
    raw_distance = pace_tab_distance_col1.number_input("Write your distance here", 1.0, value=distance, key="pace_tab_distance_col_distance")
    distance = raw_distance
    dist_unit = pace_tab_distance_col2.radio("Unit", ('m', 'km', 'mi'), index=1, key="pace_tab_distance_col_unit")
    if dist_unit == 'Kilometers (km)':
        distance *= 1000.
    elif dist_unit == 'Miles (mi)':
        distance *= 1609.34

    pace_tab_time_col.subheader("Time")
    pace_tab_time_col1, pace_tab_time_col2, pace_tab_time_col3 = pace_tab_time_col.columns(3)
    h = pace_tab_time_col1.number_input("Hours", value=0, min_value=0, key="pace_tab_time_col_hours")
    m = pace_tab_time_col2.number_input("Minutes", value=0, min_value=0, max_value=59, key="pace_tab_time_col_minutes")
    s = pace_tab_time_col3.number_input("Seconds", value=0, min_value=0, max_value=59, key="pace_tab_time_col_seconds")
    time = h * 3600 + m * 60 + s
    pace_min, pace_sec = get_pace(distance, time)
    st.header(f"Average pace: {pace_min:.0f}m{pace_sec:2.0f}s/{dist_unit}")


with distance_tab:
    distance_tab_time_col, _, distance_tab_pace_col= st.columns([10, 0.5, 8])

    distance_tab_time_col.subheader("Time")
    distance_tab_time_col1, distance_tab_time_col2, distance_tab_time_col3 = distance_tab_time_col.columns(3)
    h = distance_tab_time_col1.number_input("Hours", value=0, min_value=0, key="distance_tab_time_col_hours")
    m = distance_tab_time_col2.number_input("Minutes", value=0, min_value=0, max_value=59, key="distance_tab_time_col_minutes")
    s = distance_tab_time_col3.number_input("Seconds", value=0, min_value=0, max_value=59, key="distance_tab_time_col_seconds")
    time = h * 3600 + m * 60 + s

    distance_tab_pace_col.subheader("Pace")

    distance_tab_pace_col1, distance_tab_pace_col2 = distance_tab_pace_col.columns(2)
    pace_min = distance_tab_pace_col1.number_input("Minutes", value=0, min_value=0, max_value=59, key="distance_tab_pace_col_minutes")
    pace_sec = distance_tab_pace_col2.number_input("Seconds", value=0, min_value=0, max_value=59, key="distance_tab_pace_col_seconds")
    pace = pace_min * 60 + pace_sec

    try:
        distance = time / pace
    except ZeroDivisionError:
        distance = 0.

    st.header(f"Distance: {distance:.2f}km")


with time_tab:
    time_tab_pace_col, _, time_tab_distance_col= st.columns([8, 0.5, 8])

    time_tab_pace_col.subheader("Pace")

    column1, column2 = time_tab_pace_col.columns(2)
    pace_min = column1.number_input("Minutes", 0)
    pace_sec = column2.number_input("Seconds", 0)
    pace = pace_min * 60 + pace_sec

    time_tab_distance_col.subheader("Distance")

    default_distance = time_tab_distance_col.selectbox("Select distance", list(DISTANCES.keys()))
    distance = DISTANCES[default_distance]
    column1, column2 = time_tab_distance_col.columns([2, 1])
    raw_distance = column1.number_input("Write your distance here", 1.0, value=distance)
    distance = raw_distance
    dist_unit = column2.radio("Unit", ('m', 'km', 'mi'), index=1)
    if dist_unit == 'Kilometers (km)':
        distance *= 1000.
    elif dist_unit == 'Miles (mi)':
        distance *= 1609.34

    time = distance * pace
    h = time // 3600
    m = (time - h * 3600) // 60
    s = time % 60
    st.header(f"Time: {h:.0f}:{m:02.0f}:{s:02.0f}")

st.markdown("""---""")
