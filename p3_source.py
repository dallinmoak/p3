import os
import re
import pandas as pd
from lets_plot import *
from cleanup import cleanup

LetsPlot.setup_html(isolated_frame=True)

df_raw = pd.read_json(
    "https://github.com/byuidatascience/data4missing/raw/master/data-raw/flights_missing/flights_missing.json"
)


# working_frame = cleanup(df_raw)

# current_dir = os.getcwd()
# output_path = os.path.join(current_dir, "flights_missing_c.json")
# working_frame.to_json(output_path, orient="records", lines=False)


df = pd.read_json("flights_missing_c.json")
df.replace("", pd.NA, inplace=True)


q1_example = df[df.isna().any(axis=1)]

airport_names = (
    df.groupby("airport_code")
    .agg({"airport_name": lambda x: x.mode()[0] if not x.mode().empty else None})
    .reset_index()
)

airport_names["airport_name"] = airport_names["airport_name"].str.replace(
    r"^[^:]+:\s*", "", regex=True
)
airport_names.set_index("airport_code", inplace=True)

df["minutes_delayed_total_per_flight"] = (
    df["minutes_delayed_total"] / df["num_of_flights_total"]
).fillna(0)

q2_data = df.groupby("airport_code").agg(
    avg_delay_per_flight=("minutes_delayed_total_per_flight", "mean"),
    total_flights=("num_of_flights_total", "sum"),
    total_delays=("num_of_delays_total", "sum"),
)

q2_data["delay_percent"] = q2_data["total_delays"] / q2_data["total_flights"]

q2_data["avg_delay_per_flight_hours"] = q2_data["avg_delay_per_flight"] / 60

q3_data = df.groupby("month").agg(
    total_flights=("num_of_flights_total", "sum"),
    total_delays=("num_of_delays_total", "sum"),
)

q3_data["delay_percent"] = q3_data["total_delays"] / q3_data["total_flights"]

# please ignore the fact that this map is literally all over github; turns out that everyone uses the same numbers for mapping months 🤷.
month_mapping = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

q3_data["month_no"] = q3_data.index.map(month_mapping)
q3_data["month"] = q3_data.index
q3_data.reset_index(drop=True, inplace=True)
q3_data["month_no"] = q3_data["month_no"].astype(int)

q3_data = q3_data.sort_values("month_no")

q3_chart = (
    ggplot(q3_data, aes(x="month_no", y="delay_percent"))
    + geom_line()
    + labs(title="Monthly Flight Delay Percentage", x="Month", y="Delay Percentage")
    + scale_x_continuous(breaks=q3_data["month_no"], labels=q3_data["month"])
)
