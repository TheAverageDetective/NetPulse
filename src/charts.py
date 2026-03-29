import matplotlib
matplotlib.use("Agg")
import pandas
from matplotlib import pyplot as chart, font_manager


def generate (filepath : str, chartpath : str) :

    # Skip malformed CSV rows so one bad write does not break chart generation.
    data = pandas.read_csv(filepath, delimiter=",", on_bad_lines="skip", engine="python")
    data = data[ data["result"] != "failed" ]       # We filter out failed downloads
    data["elapsed_transfer_s"] = pandas.to_numeric(data["elapsed_transfer_s"], errors="coerce")
    data = data.dropna(subset=["timestamp", "elapsed_transfer_s"])
    if data.empty:
        print("No valid successful rows found to generate chart.")
        return

    # Use HH:MM on x-axis
    data["x-axis"] = data["timestamp"].map(lambda time : ":".join(time.split("T")[1].split(":")[:2]))
    data = data.sort_values(by=["x-axis"])

    font_path = "assets/PatrickHand-Regular.ttf"
    font_manager.fontManager.addfont(path=font_path)
    chart.rcParams["font.family"] = font_manager.FontProperties(fname=font_path, weight="bold", size="xx-large").get_name()
    chart.style.use("dark_background")
    chart.plot(data["x-axis"], data["throughput_mbps"], color="chartreuse")
    chart.title("Network speed trend", fontsize=16)
    chart.xlabel("Download time (HH:MM)", fontsize=16)
    chart.xticks(rotation=40)
    chart.tight_layout()
    chart.subplots_adjust(0.1, 0.15)
    chart.ylabel("Throughput (Mbps)", fontsize=16)

    chart.savefig(chartpath, dpi=200)
