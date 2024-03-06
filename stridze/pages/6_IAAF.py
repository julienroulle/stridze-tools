import pandas as pd
import streamlit as st

st.title("IAAF Scoring Calculator")

st.write(
    "This calculator uses the IAAF scoring tables to calculate the score for a given performance."
)

table = pd.read_csv("data/external/iaaf_2022.csv")

col1, col2, col3 = st.columns(3)

venue = col1.selectbox("Venue", table["Venue type"].unique())
gender = col2.selectbox("Gender", table["Gender"].unique())
event = col3.selectbox("Event", table["Discipline"].unique())

hours_col, minutes_col, seconds_col, hundredths_col = st.columns(4)

hours = hours_col.number_input("Hours", value=0, min_value=0, max_value=23, step=1)
minutes = minutes_col.number_input(
    "Minutes", value=0, min_value=0, max_value=59, step=1
)
seconds = seconds_col.number_input(
    "Seconds", value=0, min_value=0, max_value=59, step=1
)
hundredths = hundredths_col.number_input(
    "hundredths", value=0, min_value=0, max_value=99, step=1
)

time = hours * 3600 + minutes * 60 + seconds + hundredths / 100

factor, reference = table.loc[
    (table["Discipline"] == event)
    & (table["Gender"] == gender)
    & (table["Venue type"] == venue)
].iloc[0][["Conversion factor", "Result shift"]]

score = factor * (time + reference) ** 2

st.subheader(f"Your score is: {int(score)}")

st.header("Equivalence Table")

st.write(
    "The following table shows the equivalence between the score and the performance."
)

df = table.copy()

df["Performance"] = abs((score / df["Conversion factor"]) ** 0.5 + df["Result shift"])

df["Performance"] = pd.to_datetime(df["Performance"], unit="s").dt.strftime(
    "%H:%M:%S.%f"
)
df["Performance"] = df["Performance"].str[:-4]

df = df.drop(columns=["Conversion factor", "Result shift", "Point shift"])

st.dataframe(df, use_container_width=True)
