
# '''
# the module is responsible for loading the recorded download data from the `data/` directory
# performs statistical analysis on throughput values such as mean, median, mode and standard deviation
# identifies the busiest hour based on minimum throughput observed
# and prepares the processed results for visualization and reporting
# '''

# import os

# import pandas as pd

# # DATA_PATH = "data/test_set1.csv"

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# DATA_PATH = os.path.join(BASE_DIR, "data", "test_set1.csv")

# df = pd.read_csv(DATA_PATH)


# # column names may have leading/trailing spaces, so we strip them
# df.columns = df.columns.str.strip()

# # filter only successful downloads
# df = df[df["result"] == "success"]

# # statistics
# mean_throughput = df["throughput_mbps"].mean()
# median_throughput = df["throughput_mbps"].median()
# mode_throughput = df["throughput_mbps"].mode()[0]

# min_throughput = df["throughput_mbps"].min()
# max_throughput = df["throughput_mbps"].max()
# std_dev = df["throughput_mbps"].std()

# # busiest hour (lowest throughput)
# busiest_row = df.loc[df["throughput_mbps"].idxmin()]
# busiest_hour = busiest_row["hour_of_day"]

# print("----- Network Throughput Analysis -----")
# print(f"Mean Throughput: {mean_throughput:.2f} Mbps")
# print(f"Median Throughput: {median_throughput:.2f} Mbps")
# print(f"Mode Throughput: {mode_throughput:.2f} Mbps")
# print(f"Min Throughput: {min_throughput:.2f} Mbps")
# print(f"Max Throughput: {max_throughput:.2f} Mbps")
# print(f"Standard Deviation: {std_dev:.2f}")
# print(f"Busiest Hour: {busiest_hour}")


"""
Loads recorded download data from the `data/` directory, performs statistical
analysis on throughput values (mean, median, mode, std dev), identifies the
busiest hour (minimum throughput), and prepares results for visualization/reporting.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "test_set1.csv")

THROUGHPUT_COL = "throughput_mbps"
HOUR_COL       = "hour_of_day"
RESULT_COL     = "result"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=lambda c: c.strip() in {THROUGHPUT_COL, HOUR_COL, RESULT_COL})
    df.columns = df.columns.str.strip()
    return df[df[RESULT_COL] == "success"].reset_index(drop=True)


def analyze_throughput(df: pd.DataFrame) -> dict:
    throughput = df[THROUGHPUT_COL]
    stats = throughput.agg(["mean", "median", "min", "max", "std"])

    return {
        "mean":         stats["mean"],
        "median":       stats["median"],
        "mode":         throughput.mode().iat[0],
        "min":          stats["min"],
        "max":          stats["max"],
        "std_dev":      stats["std"],
        "busiest_hour": df.loc[throughput.idxmin(), HOUR_COL],
    }


def print_report(stats: dict) -> None:
    print("\n".join([
        "----- Network Throughput Analysis -----",
        f"Mean Throughput:    {stats['mean']:.2f} Mbps",
        f"Median Throughput:  {stats['median']:.2f} Mbps",
        f"Mode Throughput:    {stats['mode']:.2f} Mbps",
        f"Min Throughput:     {stats['min']:.2f} Mbps",
        f"Max Throughput:     {stats['max']:.2f} Mbps",
        f"Standard Deviation: {stats['std_dev']:.2f}",
        f"Busiest Hour:       {stats['busiest_hour']}",
    ]))


if __name__ == "__main__":
    df = load_data(DATA_PATH)
    stats = analyze_throughput(df)
    print_report(stats)