import asyncio

import pandas as pd
import streamlit as st

from stridze.db import engine

st.set_page_config(
    page_title="Hello", page_icon=":running_shirt_with_sash:", layout="wide"
)


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
asyncio.set_event_loop(st.session_state.loop)

system = st.sidebar.radio("Unit System", ("Metric", "Imperial"), index=0)
if system is not None:
    st.session_state["system"] = system

# activities = get_activities()
# records = get_records()
# laps = get_laps()

# activities_clm, distance_clm, hours_clm = st.columns(3)
# activities_clm.metric("Activities", f"{len(activities)}")
# distance_clm.metric("Distance", f"{activities['distance'].sum() / 1000.:.2f} km")
# hours_clm.metric("Hours", f"{activities['elapsed_time'].sum() / 3600.:.2f} h")

# from plotly import graph_objects as go

# st.write(activities.head())

# fig = go.Figure()
# fig.add_trace(
#     go.Scatter(
#         x=activities["start_time"],
#         y=activities["distance"],
#         mode="markers",
#         marker=dict(
#             size=4,
#             color=activities["average_speed"],
#             colorscale="Viridis",
#             showscale=True,
#         ),
#     )
# )
# layout = go.Layout(
#     xaxis=dict(
#         rangeslider={"visible": True},
#     ),
# )
# fig.layout = layout
# st.plotly_chart(fig)
