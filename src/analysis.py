"""
Loads recorded download data from the `data/` directory, performs statistical
analysis on throughput values (mean, median, mode, std dev), identifies the
busiest hour (minimum throughput), and prepares results for visualization/reporting.
"""

import json
import pandas as pd

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


def save_report (stats : dict, reportpath : str) -> None :
    reportfile = open(reportpath, "w")
    for key in stats.keys() :
        stats[key] = int(stats[key])
    json.dump(stats, reportfile, indent=4)
    reportfile.flush()
    reportfile.close()
    print("\nReport saved")


def analyze (filepath : str, reportpath : str) :
    df = load_data(filepath)
    stats = analyze_throughput(df)
    print_report(stats)
    save_report(stats, reportpath)

