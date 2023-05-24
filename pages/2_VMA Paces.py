import streamlit as st
import pandas as pd
import numpy as np

system = st.sidebar.radio("Unit System", ('Metric', 'Imperial'), index=0)

dist_unit = 'km'
if system is not None:
    st.session_state['system'] = system
    if st.session_state['system'] == 'Imperial':
        dist_unit = 'mi'

st.header('VMA based paces')

speed = st.number_input(f"VMA ({dist_unit}/h)", min_value=0.0, max_value=30.0, value=19.5)

pace_speed_tab, short_distance_tab, long_distance_tab, race_time_tab = st.tabs(['Pace and Speed', 'Short Distance', 'Long Distance', 'Race Times'])

with pace_speed_tab:
    pace = 3600 / speed

    vma_percentages = np.concatenate(([60], np.arange(70, 115, 5)))
    speeds = speed * vma_percentages / 100.
    paces = pace / (vma_percentages / 100)
    df = pd.DataFrame({
        'VMA': [str(elt) + ' %' for elt in vma_percentages],
        f'Speed ({dist_unit}/h)': [round(speed, 2) for speed in speeds],
        f'Paces (min/{dist_unit})': [f"{pace // 60:.0f}:{pace % 60:02.0f}" for pace in paces]
    })
    df = df.set_index('VMA')

    st.dataframe(df)

with short_distance_tab:
    pace = 3600 / speed
    vma_percentages = np.arange(85, 120, 5)
    distances = np.arange(100, 900, 100)
    paces = pace / (vma_percentages / 100)
    times = {
        f"{distance}m": [f"{pace * distance / 1000 // 60:.0f}min{pace * distance / 1000 % 60:02.1f}s" for pace in paces] for distance in distances
    }
    df = pd.DataFrame(times, index=[str(elt) + ' %' for elt in vma_percentages])
    print(df.T)
    st.dataframe(df.T, use_container_width=True)

with long_distance_tab:
    vma_percentages = np.arange(70, 105, 5)
    distances = np.arange(1000, 5100, 500)
    paces = pace / (vma_percentages / 100)
    times = {
        f"{distance}m": [f"{pace * distance / 1000 // 60:.0f}min{pace * distance / 1000 % 60:02.0f}s" for pace in paces] for distance in distances
    }
    df = pd.DataFrame(times, index=[str(elt) + ' %' for elt in vma_percentages])

    st.dataframe(df.T, use_container_width=True)

with race_time_tab:
    vma_percentages = np.arange(75, 100, 2.5)
    distances = [5., 10., 21.097, 42.195]
    paces = pace / (vma_percentages / 100)
    times = {
        f"{distance}km": [f"{pace * distance // 3600:.0f}h{pace * distance % 3600 // 60:.0f}min{pace * distance % 60:02.0f}s" for pace in paces] for distance in distances
    }
    df = pd.DataFrame(times, index=[str(elt) + ' %' for elt in vma_percentages])

    st.dataframe(df, use_container_width=True)

