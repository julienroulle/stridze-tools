import pandas as pd
from sklearn.linear_model import LinearRegression

from stridze.utils import str_time_to_num_time

# Load data
df = pd.read_csv("data/external/paces.csv")

df[["Easy Km", "Long Km"]] = df["Easy Km"].str.split("-", expand=True)

for col in df.columns[1:]:
    df[col] = df[col].apply(lambda x: str_time_to_num_time(x))

df["I Km"] = df.apply(
    lambda row: row["I Km"] if row["I Km"] != -1.0 else row["I 400m"] * 2.5, axis=1
)
df["R Km"] = df.apply(
    lambda row: row["R 800m"] * 1.25
    if row["R 800m"] != -1.0
    else row["R 600m"] * 5 / 3
    if row["R 600m"] != -1.0
    else row["R 400m"] * 2.5
    if row["R 400m"] != -1.0
    else row["R 200m"] * 5,
    axis=1,
)
df = df.drop(
    columns=[
        "T 400m",
        "I 400m",
        "I 1200m",
        "I Mile",
        "R 200m",
        "R 300m",
        "R 400m",
        "R 600m",
        "R 800m",
    ]
)

# Create VDOT powers
df["VDOT1"] = df["VDOT"]
df["VDOT2"] = df["VDOT1"] * df["VDOT1"]
df["VDOT3"] = df["VDOT2"] * df["VDOT1"]
df["VDOT4"] = df["VDOT3"] * df["VDOT1"]
df["VDOT5"] = df["VDOT4"] * df["VDOT1"]

params = []

for col in [c for c in df.columns if "VDOT" not in c]:
    # Fit model
    model = LinearRegression().fit(
        df[["VDOT1", "VDOT2", "VDOT3", "VDOT4", "VDOT5"]], df[col]
    )

    # Store model parameters
    params.append(
        [
            col,
            model.intercept_,
            model.coef_[0],
            model.coef_[1],
            model.coef_[2],
            model.coef_[3],
            model.coef_[4],
        ]
    )

# Store all parameters to csv
coefs = pd.DataFrame(
    params,
    columns=["Distance", "Intercept", "Coef1", "Coef2", "Coef3", "Coef4", "Coef5"],
)
coefs.to_csv("data/interim/vdot-to-training-paces-coefficients.csv", index=False)

df = pd.read_csv("data/external/races.csv")

for col in df.columns[1:]:
    df[col] = df[col].apply(lambda x: str_time_to_num_time(x))

# Create VDOT powers
df["VDOT1"] = df["VDOT"]
df["VDOT2"] = df["VDOT1"] * df["VDOT1"]
df["VDOT3"] = df["VDOT2"] * df["VDOT1"]
df["VDOT4"] = df["VDOT3"] * df["VDOT1"]
df["VDOT5"] = df["VDOT4"] * df["VDOT1"]

params = []

for col in [c for c in df.columns if "VDOT" not in c]:
    # Fit model
    model = LinearRegression().fit(
        df[["VDOT1", "VDOT2", "VDOT3", "VDOT4", "VDOT5"]], df[col]
    )

    # Store model parameters
    params.append(
        [
            col,
            model.intercept_,
            model.coef_[0],
            model.coef_[1],
            model.coef_[2],
            model.coef_[3],
            model.coef_[4],
        ]
    )

# Store all parameters to csv
coefs = pd.DataFrame(
    params,
    columns=["Distance", "Intercept", "Coef1", "Coef2", "Coef3", "Coef4", "Coef5"],
)
coefs.to_csv("data/interim/vdot-to-race-paces-coefficients.csv", index=False)
