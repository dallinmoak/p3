import os
import pandas as pd
from lets_plot import *

LetsPlot.setup_html(isolated_frame=True)

df_raw = pd.read_json(
    "https://github.com/byuidatascience/data4missing/raw/master/data-raw/flights_missing/flights_missing.json"
)


def cleanup(df_input):
    working_frame = df_input.copy()
    flight_columns_dic = {
        "airport_code": "string",
        "airport_name": "string",
        "month": "string",
        "year": "int64",
        "num_of_flights_total": "int64",
        "num_of_delays_carrier": "int64",
        "num_of_delays_late_aircraft": "int64",
        "num_of_delays_nas": "int64",
        "num_of_delays_security": "int64",
        "num_of_delays_weather": "int64",
        "num_of_delays_total": "int64",
        "minutes_delayed_carrier": "int64",
        "minutes_delayed_late_aircraft": "int64",
        "minutes_delayed_nas": "int64",
        "minutes_delayed_security": "int64",
        "minutes_delayed_weather": "int64",
        "minutes_delayed_total": "int64",
    }

    for col, dtype in flight_columns_dic.items():
        if col not in working_frame.columns:
            working_frame[col] = pd.NA

    for col, dtype in flight_columns_dic.items():
        if dtype == "int64":
            working_frame[col] = working_frame[col].fillna(0)
            # i figure i'll cast as a string first and then extract only numeric chars
            working_frame[col] = working_frame[col].astype("string")
            working_frame[col] = (
                working_frame[col].str.extract(r"(\d+)", expand=False).fillna(0)
            )

    for col, dtype in flight_columns_dic.items():
        # astype(int is gonna fail if it's NA or something weird, so if this line doesn't execute, i know i still need to clean up stuff)
        working_frame[col] = working_frame[col].astype(dtype)

    # catching a specific misspelling i found
    working_frame["month"] = working_frame["month"].replace("Febuary", "February")

    # if a month isn't specified, that row is not relevant and will be excluded.
    working_frame = working_frame[working_frame["month"] != "n/a"]

    # here's how I'm checking to make sure all months are valid:
    # possible_months = [
    #     "January",
    #     "February",
    #     "March",
    #     "April",
    #     "May",
    #     "June",
    #     "July",
    #     "August",
    #     "September",
    #     "October",
    #     "November",
    #     "December",
    # ]
    # invalid_month_filter = working_frame["month"].apply(lambda x: x not in possible_months)
    # invalid_months = working_frame[invalid_month_filter]
    # invalid_month_count = len(invalid_months)

    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, "flights_missing_c.json")
    working_frame.to_json(output_path, orient="records", lines=False)


cleanup(df_raw)

df = pd.read_json("flights_missing_c.json")
df.replace("", pd.NA, inplace=True)

# print(df.to_string())

# q1_example = df[df.isna().any(axis=1)]
