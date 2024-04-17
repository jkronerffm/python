import schedule
import time
import datetime
import threading
import logging

class Scheduler:
    def __init__(self):
        self.callbacks = []
        self.actionCallbacks = {}
        self.jobs = []
        
    def addCallback(self,callback):
        self.callbacks.append(callback)

    def addActionCallback(self, action, callback):
        self.actionCallbacks[action] = callback
        
    def addJob(self,job):
        self.jobs.append(job)
        
    def job(self, action):
        logging.debug(f"{self.__class__.__name__}.job(action={action})")
        for cb in self.callbacks:
            cb(action)
        if action in self.actionCallbacks:
            self.actionCallbacks[action]()
   
    class Thread(threading.Thread):
        Stop = threading.Event()
        Interval = 1
        @classmethod
        def run(cls):
            logging.debug(f"\nenter {cls.__name__}.run()")
            while not Scheduler.Thread.Stop.is_set():
                schedule.run_pending()
                time.sleep(cls.Interval)
            logging.debug(f"\nleave {cls.__name__}.run()")

    def start(self):
        for job, params in self.jobs:
            job.do(self.job, params)
        self._thread = Scheduler.Thread()
        self._thread.start()

    def stop(self):
        self._thread.Stop.set()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    def jobCb(action):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"jobCb(now={now},action={action})")

    def onCb():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"onCb(now={now})")

    def offCb():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"offCb(now={now})")

        
    now = datetime.datetime.now()
    on = datetime.timedelta(seconds=30)
    off = datetime.timedelta(minutes=1)
    nowon = (now + on).strftime("%H:%M:%S")
    nowoff = (now + off).strftime("%H:%M:%S")
    print(nowon, nowoff)
    waitjob = schedule.every(5).seconds
    scheduler = Scheduler()
    scheduler.addJob((waitjob,'wait'))
    scheduler.addCallback(jobCb)
    offJob = schedule.every().day.at(nowoff)
    scheduler.addJob((offJob, "off"))
    scheduler.addActionCallback("off", offCb)
    onJob = schedule.every().day.at(nowon)
    scheduler.addJob((onJob, "on"))
    scheduler.addActionCallback("on", onCb)
    scheduler.start()
    print(f"wait since {datetime.datetime.now()}")
    time.sleep(2*60)
    print(f"waiting is over at {datetime.datetime.now()}")
    scheduler.stop()
    print("done")

