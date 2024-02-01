import asyncio
import datetime

import extra_streamlit_components as stx
import pandas as pd
import streamlit as st

from stridze.db import engine

st.set_page_config(
    page_title="Hello", page_icon=":running_shirt_with_sash:", layout="wide"
)


st.write("# Cookie Manager")


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()

st.subheader("All Cookies:")
cookies = cookie_manager.get_all()
st.write(cookies)

c1, c2, c3 = st.columns(3)


@st.cache_resource()
def get_db_connection():
    return engine.connect()


conn = get_db_connection()


@st.cache_data(show_spinner=False)
def get_activities():
    df = pd.read_sql_table("activity", conn)
    df = df.loc[
        df["activity_type"].isin(["running", "trail_running", "treadmill_running"])
    ]
    print(df.activity_type.unique())
    return df


@st.cache_data(show_spinner=False)
def get_records():
    df = pd.read_sql_table("record", conn)
    return df


@st.cache_data(show_spinner=False)
def get_laps():
    df = pd.read_sql_table("lap", conn)
    return df


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

st.image(
    "/Users/julienroulle/dev/stridze-tools/assets/fitsum-admasu-oGv9xIl7DkY-unsplash.jpg",
    use_column_width=True,
)
