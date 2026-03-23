# cn-banana
CN Banana project, team 12 project 15

Download interval is 1 minute by default.

---
> Files

```txt
main.py             Manages all the logic
dl_thread.py        Creates a separate thread to download the file at
                    intervals to avoid blocking the main thread
fetch-resource.py   Downloads the file once and stores metrics in csv

charts.py           Generates a chart from the csv for visualization
```

___
> Install dependencies
```ps1
pip install -r requirements.txt
```

___
> Run code

- windows
```ps1
python main.py --url <download_url> --time <download_interval_minutes>
```
- linux
```ps1
python3 main.py --url <download_url> --time <download_interval_minutes>
```

___

