import threading, time, sched

schedule = sched.scheduler()
nextrun : sched.Event | None = None

scheduler_thread = threading.Thread(target=schedule.run, daemon=True)
scheduler_thread_stopped = threading.Event()


def run_download (interval : int) :
    print("Downloading at time", time.localtime(time.time()))
    if not scheduler_thread_stopped.is_set():
        schedule.enterabs(time.time() + (interval * 60), 1, run_download, [interval])
        # TODO: call runner here


def start (interval : int) :
    schedule.enter(0, 1, run_download, [interval])
    scheduler_thread.start()


def stop () :
    scheduler_thread_stopped.set()
    if nextrun != None : schedule.cancel(nextrun)

