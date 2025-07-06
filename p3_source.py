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

q4_data_raw = df.copy()

average_weather_rates = {
    "january": {
        "late": 0.3,
        "nas": 0.4,
    },
    "february": {
        "late": 0.3,
        "nas": 0.4,
    },
    "march": {
        "late": 0.3,
        "nas": 0.4,
    },
    "april": {
        "late": 0.3,
        "nas": 0.65,
    },
    "may": {
        "late": 0.3,
        "nas": 0.65,
    },
    "june": {
        "late": 0.3,
        "nas": 0.65,
    },
    "july": {
        "late": 0.3,
        "nas": 0.65,
    },
    "august": {
        "late": 0.3,
        "nas": 0.65,
    },
    "september": {
        "late": 0.3,
        "nas": 0.4,
    },
    "october": {
        "late": 0.3,
        "nas": 0.4,
    },
    "november": {
        "late": 0.3,
        "nas": 0.4,
    },
    "december": {
        "late": 0.3,
        "nas": 0.4,
    },
}

q4_data_raw["delays_late_aircraft_weather_extrapolated"] = (
    q4_data_raw["month"]
    .str.lower()
    .map(lambda month: average_weather_rates[month]["late"])
    * q4_data_raw["num_of_delays_late_aircraft"]
)

q4_data_raw["delays_nas_weather_extrapolated"] = (
    q4_data_raw["month"]
    .str.lower()
    .map(lambda month: average_weather_rates[month]["nas"])
    * q4_data_raw["num_of_delays_nas"]
)

q4_data_raw["delays_weather_mild_total"] = (
    q4_data_raw["delays_late_aircraft_weather_extrapolated"]
    + q4_data_raw["delays_nas_weather_extrapolated"]
)

q4_data_raw["delays_weather_all"] = (
    q4_data_raw["delays_weather_mild_total"] + q4_data_raw["num_of_delays_weather"]
)


q4_data = q4_data_raw[
    [
        "airport_code",
        "month",
        "year",
        "num_of_flights_total",
        "num_of_delays_total",
        "num_of_delays_late_aircraft",
        "delays_late_aircraft_weather_extrapolated",
        "num_of_delays_nas",
        "delays_nas_weather_extrapolated",
        "delays_weather_mild_total",
        "num_of_delays_weather",
        "delays_weather_all",
    ]
].rename(
    columns={
        "num_of_flights_total": "total_flights",
        "num_of_delays_total": "total_delays",
        "num_of_delays_late_aircraft": "late_delays",
        "num_of_delays_nas": "nas_delays",
        "delays_late_aircraft_weather_extrapolated": "late_weather_ext",
        "delays_nas_weather_extrapolated": "nas_weather_ext",
        "delays_weather_mild_total": "weather_mild_total",
        "num_of_delays_weather": "weather_severe",
        "delays_weather_all": "weather_all",
    }
)

q5_data = q4_data.groupby("airport_code").agg(
    total_flights=("total_flights", "mean"),
    total_delays=("total_delays", "mean"),
    delays_weather=("weather_all", "mean"),
    delays_weather_mild=("weather_mild_total", "mean"),
    delays_weather_severe=("weather_severe", "mean"),
)

q5_data["delay_rate"] = q5_data["total_delays"] / q5_data["total_flights"]

q5_data["weather_delay_rate"] = q5_data["delays_weather"] / q5_data["total_flights"]

q5_data["weather_mild_delay_rate"] = (
    q5_data["delays_weather_mild"] / q5_data["total_flights"]
)

q5_data["weather_severe_delay_rate"] = (
    q5_data["delays_weather_severe"] / q5_data["total_flights"]
)

q5_data_display = q5_data[
    [
        "weather_delay_rate",
        "weather_mild_delay_rate",
        "weather_severe_delay_rate",
    ]
].reset_index()

q5_data_melted = q5_data_display.melt(
    id_vars="airport_code",
    value_vars=["weather_mild_delay_rate", "weather_severe_delay_rate"],
    var_name="delay_type",
    value_name="delay_rate",
).sort_values(by=["airport_code", "delay_type"])

q5_chart = (
    ggplot(
        data=q5_data_melted,
        mapping=aes(x="airport_code", y="delay_rate", fill="delay_type"),
    )
    + geom_bar(stat="identity", position="stack")
    + labs(
        title="Average Monthly Weather Delay Rates by Airport",
        x="Airport Code",
        y="Weather Delay Rate",
        fill="Delay Type",
    )
)
