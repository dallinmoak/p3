import os
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
