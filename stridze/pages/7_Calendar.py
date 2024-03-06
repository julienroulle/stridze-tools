# import numpy as np
# import pandas as pd
# import streamlit as st
# from sqlmodel import Session, select

# from stridze.db import engine
# from stridze.db.models import Activity

# session = Session(engine)


# FCM = 192 - 0.007 * 28**2
# FCR = 42


# def calculate_trimp(hr, t):
#     # Fix missing values by interpolation
#     hr = hr.interpolate()
#     hr = (np.array(hr) - FCR) / (FCM - FCR)

#     if len(hr) == 0:
#         print("No HR data")
#         return np.NaN
#     else:
#         t = np.diff(t) / 1000000000
#         t = t.astype(float)
#         # Trim elapsed seconds to 0.5min
#         t = [min(elt / 60.0, 0.5) for elt in t]

#         if len(hr) < len(t):
#             t = t[: len(hr)]
#         elif len(hr) > len(t):
#             hr = hr[: len(t)]

#         return np.sum(t * hr * 0.64 * np.exp(1.92 * hr))


# # activities = session.exec(select(Activity)).all()

# # # make a dropdown with list of activities
# # activity = st.selectbox(
# #     "Select an activity", activities, format_func=lambda x: x.start_time
# # )


# # # display the activity
# # st.write(activity)
# @st.cache_data
# def load_activities():
#     return pd.read_sql_table("activity", con=engine)


# @st.cache_data
# def load_records():
#     return pd.read_sql_table("record", con=engine)


# # Load activities with caching
# activities = load_activities()

# # Load records with caching
# records = load_records()

# records = records.sort_values(by=["timestamp"])
# records.distance /= 1000
# records.enhanced_speed *= 3.6

# activities = activities.loc[
#     activities["activity_type"].isin(["running", "trail_running"])
# ]

# activities["trimp"] = activities.apply(
#     lambda row: calculate_trimp(
#         records.loc[records["activity_id"] == row["id"]]["heart_rate"],
#         records.loc[records["activity_id"] == row["id"]]["timestamp"],
#     ),
#     axis=1,
# )

# activities.start_time = pd.to_datetime(activities.start_time)
# m = activities.set_index("start_time")

# m = m.groupby(pd.Grouper(freq="D")).sum()

# st.bar_chart(m.distance.iloc[-26:])
# st.line_chart(m.trimp.iloc[-26:])

# bins = pd.cut(records["enhanced_speed"], bins=np.arange(0, 30, 1))

# grouped = records.groupby(bins)["distance"].sum().reset_index()
# # grouped['enhanced_speed'] = pd.IntervalIndex(grouped['enhanced_speed']).mid
# st.write(grouped)
# st.bar_chart(grouped, y="distance")
