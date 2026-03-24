import pandas
from matplotlib import pyplot as chart, font_manager


def generate (filepath : str, chartpath : str) :

    data = pandas.read_csv(filepath, delimiter=",")
    data = data[ data["result"] != "failed" ]       # We filter out failed downloads

    # Use HH:MM on x-axis
    data["x-axis"] = data["timestamp"].map(lambda time : ":".join(time.split("T")[1].split(":")[:2]))
    data = data.sort_values(by=["x-axis"])

    font_path = "assets/PatrickHand-Regular.ttf"
    font_manager.fontManager.addfont(path=font_path)
    chart.rcParams["font.family"] = font_manager.FontProperties(fname=font_path, weight="bold", size="xx-large").get_name()
    chart.style.use("dark_background")
    chart.plot(data["x-axis"], data["elapsed_transfer_s"], color="chartreuse")
    chart.title("Network speed trend", fontsize=16)
    chart.xlabel("Download time (HH:MM)", fontsize=16)
    chart.ylabel("Throughput (Mbps)", fontsize=16)

    chart.savefig(chartpath, dpi=200)
