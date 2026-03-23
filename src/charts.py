import pandas
from matplotlib import pyplot as chart, font_manager


def generate (filepath : str, chartpath : str) :

    data = pandas.read_csv(filepath, delimiter=",")
    data = data[ data["result"] != "failed" ]       # We filter out failed downloads

    # When actually running this project, we may not actually be waiting for a whole hour
    # to pass for the download to happen. We may be doing it every few minutes instead.
    # So, there will be multiple rows that have the same data[hour_of_day].
    # It would not make sense to plot a graph with multiple data points in the same hour.
    # That will create a vertical straight line.
    # I instead use the hour and minute (extracted from data[timestamp] below)
    x_axis = data["timestamp"].map(lambda time : ":".join(time.split("T")[1].split(":")[:2]))

    font_path = "assets/PatrickHand-Regular.ttf"
    font_manager.fontManager.addfont(path=font_path)
    chart.rcParams["font.family"] = font_manager.FontProperties(fname=font_path, weight="bold", size="xx-large").get_name()
    chart.style.use("dark_background")
    chart.plot(x_axis, data["elapsed_transfer_s"], color="chartreuse")
    chart.title("Network speed trend", fontsize=16)
    chart.xlabel("Download time (HH:MM)", fontsize=16)
    chart.ylabel("Throughput (Mbps)", fontsize=16)

    chart.savefig(chartpath, dpi=200)
