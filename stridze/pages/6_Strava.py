import base64

import altair as alt
import streamlit as st
import sweat
from pandas.api.types import is_numeric_dtype

import stridze.strava as strava

st.set_page_config(
    page_title="Streamlit Activity Viewer for Strava",
    page_icon=":circus_tent:",
)

st.image("https://analytics.gssns.io/pixel.png")

strava_header = strava.header()

st.markdown(
    """
    # :circus_tent: Streamlit Activity Viewer for Strava
    This is a proof of concept of a [Streamlit](https://streamlit.io/) application that implements the [Strava API](https://developers.strava.com/) OAuth2 authentication flow.
    """
)

strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)

if strava_auth is None:
    st.markdown(
        'Click the "Connect with Strava" button at the top to login with your Strava account and get started.'
    )
    st.stop()


# activity = strava.select_strava_activity(strava_auth)
# activity_list = strava.download_all_activities(strava_auth)
# st.write(f"Found {len(activity_list)} activities")
# data = strava.download_activity(activity, strava_auth)

from stridze.db import get_session
from stridze.db.models import Strava
from stridze.db.schemas.strava import StravaSchema

session = get_session()

from ratelimit import limits, sleep_and_retry


@sleep_and_retry
@limits(calls=15, period=900)
def process_activity(activity, strava_auth, session):
    data = sweat.read_strava(activity["id"], strava_auth["access_token"])
    for timestamp, row in data.iterrows():
        d = row.to_dict()
        d["timestamp"] = timestamp
        d["user_id"] = strava_auth["athlete"]["id"]
        d["activity_id"] = activity["id"]
        d["activity_type"] = activity["sport_type"]
        d = StravaSchema.parse_obj(d)
        d = Strava(**d.dict())
        session.add(d)
    session.commit()


# Iterate over the activities with rate limiting
@sleep_and_retry
@limits(calls=15, period=900)
def download_all_activities(auth):
    activity_page = 1
    activities = strava.get_activities(auth=auth, page=activity_page)
    while activities:
        print(activities)
        print(f"Downloading page {activity_page}")
        activity_page += 1
        activities = strava.get_activities(auth=auth, page=activity_page)

        for idx, activity in enumerate(activities):
            with st.spinner(
                f"Downloading activity {activity['id']} - \"{activity['name']}\"..."
            ):
                if (
                    session.query(Strava)
                    .filter(Strava.activity_id == activity["id"])
                    .first()
                ):
                    continue
                process_activity(activity, strava_auth, session)


download_all_activities(strava_auth)
# csv = data.to_csv()
# csv_as_base64 = base64.b64encode(csv.encode()).decode()
# st.markdown(
#     (
#         f"<a "
#         f'href="data:application/octet-stream;base64,{csv_as_base64}" '
#         f"download=\"{activity['id']}.csv\" "
#         f'style="color:{strava.STRAVA_ORANGE};"'
#         f">Download activity as csv file</a>"
#     ),
#     unsafe_allow_html=True,
# )


# columns = []
# for column in data.columns:
#     if is_numeric_dtype(data[column]):
#         columns.append(column)

# selected_columns = st.multiselect(label="Select columns to plot", options=columns)

# data["index"] = data.index

# if selected_columns:
#     for column in selected_columns:
#         altair_chart = (
#             alt.Chart(data)
#             .mark_line(color=strava.STRAVA_ORANGE)
#             .encode(
#                 x="index:T",
#                 y=f"{column}:Q",
#             )
#         )
#         st.altair_chart(altair_chart, use_container_width=True)
# else:
#     st.write("No column(s) selected")
