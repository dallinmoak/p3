import os
import pandas as pd


def cleanup(df_input):
    working_frame = df_input.copy()
    flight_columns_dic = {
        "airport_code": "string",
        "airport_name": "string",
        "month": "string",
        "year": "Int64",
        "num_of_flights_total": "Int64",
        "num_of_delays_carrier": "Int64",
        "num_of_delays_late_aircraft": "Int64",
        "num_of_delays_nas": "Int64",
        "num_of_delays_security": "Int64",
        "num_of_delays_weather": "Int64",
        "num_of_delays_total": "Int64",
        "minutes_delayed_carrier": "Int64",
        "minutes_delayed_late_aircraft": "Int64",
        "minutes_delayed_nas": "Int64",
        "minutes_delayed_security": "Int64",
        "minutes_delayed_weather": "Int64",
        "minutes_delayed_total": "Int64",
    }

    for col, dtype in flight_columns_dic.items():
        if col not in working_frame.columns:
            working_frame[col] = pd.NA

    for col, dtype in flight_columns_dic.items():
        if dtype == "Int64":
            working_frame[col] = working_frame[col].fillna("")
            # i figure i'll cast as a string first and then extract only numeric chars
            working_frame[col] = working_frame[col].astype("string")
            working_frame[col] = working_frame[col].str.extract(r"(\d+)", expand=False)

    # i know at this point there might be some empty strings in int columns, so i will replace them with pandas.NA
    for col, dtype in flight_columns_dic.items():
        working_frame[col] = working_frame[col].replace("", pd.NA)

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

    return working_frame
