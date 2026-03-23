"""
This code will schedule the download to run at an interval.
The scheduling and download happens on a separate thread from the main thread.
"""

import threading, time, sched
from . import fetch_resource


schedule = sched.scheduler(time.time, time.sleep)
nextrun : sched.Event | None = None

scheduler_thread = threading.Thread(target=schedule.run, daemon=True)
scheduler_thread_stopped = threading.Event()


def run_download (url : str, file : str, interval: int, next_time : int) :
    global nextrun
    print("Downloading at time", time.localtime().tm_hour)

    if not scheduler_thread_stopped.is_set():
        next_time += interval * 60
        nextrun = schedule.enterabs(next_time, 1, run_download, [url, file, interval, next_time])
        fetch_resource.runner(url, file)


def start (url : str, interval : int, file: str) :
    schedule.enterabs(time.time(), 1, run_download, [url, file, interval, time.time()])
    scheduler_thread.start()


def stop () :
    scheduler_thread_stopped.set()
    if nextrun is not None : schedule.cancel(nextrun)
