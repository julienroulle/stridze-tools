import streamlit as st

st.set_page_config(
    page_title="GPX Analyzer",
    page_icon="👋",
)

import pandas as pd
import numpy as np
import gpxpy

import datetime
import plotly.express as px
import plotly.graph_objects as go

import pydeck as pdk

from geopy import distance
import srtm

from scipy.signal import find_peaks

_ZOOM_LEVELS = [
    360,
    180,
    90,
    45,
    22.5,
    11.25,
    5.625,
    2.813,
    1.406,
    0.703,
    0.352,
    0.176,
    0.088,
    0.044,
    0.022,
    0.011,
    0.005,
    0.003,
    0.001,
    0.0005,
    0.00025,
]


def pace_elevation(distance, slope, pace, uphill_effort):
    # https://www.runnersworld.com/advanced/a20820206/downhill-all-the-way/
    """dist (m), time (sec), temp (C)"""
    coef = 0.033 * slope
    if slope < 0:
        coef *= 0.55
    else:
        coef *= 7.5 - uphill_effort

    # delta_elev = slope * c * pace
    duration = distance * pace.seconds / 1000
    adjusted_duration = duration * (1 + coef)
    return float(adjusted_duration)


def smooth_fn(x, window_len, window='blackman'):
    """smooth function

    :param x: parameter of the function
    :type x: array
    :param window_len: window length
    :type window_len: int
    :param window: boundary to calculate
    :type window: array
    :raises ValueError: if numbers are outside of expected boundary
    :raises ValueError: if numbers are outside of expected boundary
    :return: result
    :rtype: array
    """
    x = np.asanyarray(x)

    if x.ndim != 1:
        raise ValueError

    if x.size < window_len:
        return x

    if window_len < 3:
        return x

    if window not in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]
    if window == "flat":
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")

    return y[(window_len//2-1):-(window_len//2)]


uploaded_file = st.file_uploader('Upload a GPX')

if uploaded_file is not None:
    gpx_data = gpxpy.parse(uploaded_file)

    elevation_data = srtm.get_data()
    elevation_data.add_elevations(gpx_data, smooth=True)

    len_tracks = len(gpx_data.tracks)
    len_segments = len(gpx_data.tracks[0].segments)
    len_points = len(gpx_data.tracks[0].segments[0].points)

    gpx_points = gpx_data.tracks[0].segments[0].points

    df = pd.DataFrame(columns=['lon', 'lat', 'elev', 'time']) # create a new Pandas dataframe object with give column names
    df = df.drop(columns=['time'])

    # loop through the points and append their attributes to the dataframe
    for point in gpx_points:
        df = pd.concat([df, pd.DataFrame({'lon' : point.longitude, 'lat' : point.latitude, 'elev' : point.elevation}, index=[0])], ignore_index=True)

    min_lat = df['lat'].min()
    max_lat = df['lat'].max()
    min_lon = df['lon'].min()
    max_lon = df['lon'].max()
    center_lat = (max_lat + min_lat) / 2.0
    center_lon = (max_lon + min_lon) / 2.0
    range_lon = abs(max_lon - min_lon)
    range_lat = abs(max_lat - min_lat)

    if range_lon > range_lat:
        longitude_distance = range_lon
    else:
        longitude_distance = range_lat

    zoom = 12
    for i in range(len(_ZOOM_LEVELS) - 1):
        if _ZOOM_LEVELS[i + 1] < longitude_distance <= _ZOOM_LEVELS[i]:
            zoom = i

    dist = [0]
    for idx in range(1, len(gpx_points)): # index will count from 1 to lenght of dataframe, beginning with the second row
        start = gpx_points[idx-1]
        end = gpx_points[idx]
        dist.append(distance.distance((start.latitude, start.longitude), (end.latitude, end.longitude)).m)
    
    df['segment_distance'] = dist
    dist = np.cumsum(dist)
    df['cumulative_distance'] = dist

    st.write(f"Length Geo2d: {df.cumulative_distance.iloc[-1]:.0f}m")

    df['elevation_diff'] = df['elev'].diff().fillna(0)

    st.write(f"Elevation Gain: {round(sum(df[df['elevation_diff'] > 0]['elevation_diff']), 2)}")

    st.header('Time objective')
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    race_hour_time = col1.number_input('Hours', min_value=0, max_value=24, step=1)
    race_minute_time = col2.number_input('Minutes', min_value=0, max_value=60, step=1)
    race_second_time = col3.number_input('Seconds', min_value=0, max_value=60, step=1)

    race_time = datetime.timedelta(hours=race_hour_time, minutes=race_minute_time, seconds=race_second_time)
    pace = race_time / df.cumulative_distance.iloc[-1] * 1000
    st.subheader(f"Pace: {str(pace).split('.')[0]} min/km")

    total_distance = df.cumulative_distance.iloc[-1]
    total_elevation = sum(df[df['elevation_diff'] > 0]['elevation_diff'])

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=zoom*2,
            ),
        ],
    ))

    window = st.slider("Smoothing window (m)", min_value=0, max_value=int(df.cumulative_distance.iloc[-1] // 250 // 10 * 10), value=50, step=10)


    fig_2 = px.line(df, x='cumulative_distance', y='elev', template='plotly_dark')

    # smooth = savgol_filter(df.elev.values, window_length=window, polyorder=5)
    smooth = smooth_fn(df.elev.values, window_len=window)

    #find the maximums
    peaks_idx_max, _ = find_peaks(smooth, prominence = 0.1)

    #reciprocal, so mins will become max
    smooth_rec = 1 / smooth

    #find the mins now
    peaks_idx_mins, _ = find_peaks(smooth_rec, prominence = 0.0001)

    peaks = sorted(np.concatenate([[0, len(df) - 1], peaks_idx_max, peaks_idx_mins]))


    fig_3 = px.line(x=df['cumulative_distance'], y=smooth, template='plotly_dark', labels={'x': 'Distance', 'y': 'Elevation'})
    fig_3.update_traces(line_color='red', line_width=1)

    fig_4 = px.scatter(x=df['cumulative_distance'][peaks], y=smooth[peaks])
    # st.plotly_chart(fig_4)

    fig_5 = go.Figure(data=fig_2.data + fig_3.data + fig_4.data)
    st.plotly_chart(fig_5)

    col1, col2 = st.columns(2)
    splits = col1.slider("Negative Split (%)", min_value=-25., max_value=25., value=0., step=0.5)
    uphill_effort = col2.slider("Uphill Perceived Effort", min_value=0., max_value=10., value=5., step=.5)

    elev_df = df.copy()
    elev_df['smooth_elevation'] = smooth
    elev_df = elev_df.iloc[peaks]
    elev_df = elev_df.diff().iloc[1:][['cumulative_distance', 'smooth_elevation']]
    elev_df['segment_distance'] = elev_df['cumulative_distance']
    elev_df['cumulative_distance'] = elev_df.segment_distance.cumsum()
    elev_df['grade'] = elev_df['smooth_elevation'] / elev_df['segment_distance'] * 100

    elev_df['time'] = elev_df.apply(lambda row: pace_elevation(row.segment_distance, row.grade, pace, uphill_effort), axis=1)
    estimated_time = elev_df.time.sum()
    time_ratio = race_time.seconds / estimated_time
    elev_df['time'] *= time_ratio

    elev_df['pace'] = elev_df['time'] / elev_df['segment_distance'] * 1000

    # def adjust_pace(df, splits, uphill_effort):


    # elev_df['adjusted_pace'] = adjust_pace(elev_df, splits, uphill_effort)
    mid_distance = total_distance / 2
    elev_df['pace'] = elev_df['pace'] * (1 - splits / 100 * (mid_distance - elev_df['cumulative_distance']) / mid_distance)
    # elev_df['effort_adjusted_pace'] = elev_df['split_adjusted_pace'] * (1 - uphill_effort / 100 * (mid_distance - elev_df['cumulative_distance']) / mid_distance)

    st.write(elev_df)


    display_df = pd.DataFrame()
    display_df['Split distance'] = elev_df.segment_distance.apply(lambda row: f"{row / 1000:.3f} km")
    display_df['Elevation'] = elev_df.smooth_elevation.apply(lambda row: f"{row:.0f} m")
    display_df['Pace'] = elev_df.pace.apply(lambda row: f"{row // 60:.0f}:{row % 60:02.0f} min/km")
    display_df['Duration'] = elev_df.apply(lambda row: f"{row.segment_distance / 1000 * row.pace // 60:.0f}:{row.segment_distance / 1000 * row.pace % 60:02.0f} min", axis=1)
    display_df = display_df.reset_index().drop(columns='index')
    st.dataframe(display_df, use_container_width=True)

    st.download_button(
        "Press to download splits to csv file",
        display_df.to_csv(index=False).encode('utf-8'),
        "file.csv",
        "text/csv",
        key='download-csv'
    )
