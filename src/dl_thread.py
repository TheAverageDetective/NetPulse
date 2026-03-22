import threading, time, sched, datetime

schedule = sched.scheduler(time.time, time.sleep)
nextrun : sched.Event | None = None

scheduler_thread = threading.Thread(target=schedule.run, daemon=True)
scheduler_thread_stopped = threading.Event()


def run_download (interval: int, next_time : int) :
    global nextrun
    print("Downloading at time", time.localtime().tm_hour)
    if not scheduler_thread_stopped.is_set():
        next_time += interval * 60
        nextrun = schedule.enterabs(next_time, 1, run_download, [interval, next_time])
        # TODO: call runner here
        print("Running hahahah")


def start (interval : int) :
    schedule.enterabs(time.time(), 1, run_download, [interval, time.time()])
    scheduler_thread.start()


def stop () :
    scheduler_thread_stopped.set()
    if nextrun is not None : schedule.cancel(nextrun)

