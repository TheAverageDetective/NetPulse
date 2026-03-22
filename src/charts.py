import pandas, numpy
from matplotlib import pyplot as chart

data = pandas.read_csv("../data/test_set.csv", delimiter=",")
total_rows = data["timestamp"].count()

data = data[ data["result"] != "failed" ]       # We filter out failed downloads
success_rows = data["timestamp"].count()


# print(data)
print("Failed rows: ", total_rows - success_rows)


chart.style.use("dark_background")
chart.plot(data["hour_of_day"], data["elapsed_transfer_s"], color="chartreuse")

chart.savefig("../data/chart.jpg")


