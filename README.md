# NetPulse

A python-based network client that downloads the same file every hour over a 24-hour period and analyzes download speed patterns to identify network congestion trends.

Download interval is 1 minute by default. (Can be configured via cli)

---
> Files

```txt
server.py           Hosts the web interface
main.py             Manages all the logic

src/dl_thread.py        Creates a separate thread to download the file at
                    intervals to avoid blocking the main thread
src/fetch-resource.py   Downloads the file once and stores metrics in csv

src/charts.py           Generates a chart from the csv for visualization
```

___
> Install dependencies
```ps1
pip install -r requirements.txt
```

___
> Run code (Web Interface)

- windows
```ps1
python server.py
```
- linux
```ps1
python3 server.py
```
___
> Run code

- windows
```ps1
python main.py [--url <download_url>] [--time <download_interval_minutes>]
```
- linux
```ps1
python3 main.py [--url <download_url>] [--time <download_interval_minutes>]
```
___

