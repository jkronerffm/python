import schedule
import time
import datetime
import threading
import logging

class SimpleScheduler:
    def __init__(self, loopCount = 1000):
        logging.debug(f"{self.__class__.__name__}.__init__()")
        self.callbacks = []
        self.actionCallbacks = {}
        self.jobs = []
        self._loopCount = loopCount

    @property
    def loopCount(self):
        return self._loopCount

    @loopCount.setter
    def loopCount(self, value):
        self._loopCount = value
        
    def addCallback(self,callback):
        self.callbacks.append(callback)

    def addActionCallback(self, action, callback):
        logging.debug(f"{self.__class__.__name__}.addActionCallback(action={action},callback={callback})")
        self.actionCallbacks[action] = callback
        
    def addJob(self,job):
        logging.debug(f"{self.__class__.__name__}.addJob(job={job})")
        self.jobs.append(job)    
        job[0].do(self.job,job[1])
        return job[0]

    def addJobs(self, job):
        logging.debug(f"{self.__class__.__name__}.addJob(job={job})")
        result = None
        for aJob in job[0]:
            result = self.addJob((aJob, job[1]))
        return result
                        
    def job(self, action):
        logging.debug(f"{self.__class__.__name__}.job(action={action})")
        for cb in self.callbacks:
            cb(action)
        if action in self.actionCallbacks:
            self.actionCallbacks[action]()
            logging.debug(f"{self.__class__.__name__}.job(action={action}) back from actionCallback")
   
    class Thread(threading.Thread):
        LoopCount = 1000
        Stop = threading.Event()
        Interval = 3
        @classmethod
        def run(cls):
            logging.debug(f"\nenter {cls.__name__}.run()")
            count = 0
            while not SimpleScheduler.Thread.Stop.is_set():
                count+= 1
                if (count % cls.LoopCount) == 0:
                    logging.debug(f"{cls.__name__}.run() in loop")
                    count = 0
                schedule.run_pending()
                time.sleep(cls.Interval)
            logging.debug(f"\nleave {cls.__name__}.run()")

    def start(self):
        logging.debug(f"{self.__class__.__name__}.start()")
        SimpleScheduler.Thread.LoopCount = self.loopCount
        self._thread = SimpleScheduler.Thread()
        self._thread.start()

    def stop(self):
        self._thread.Stop.set()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    def jobCb(action):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"jobCb(now={now},action={action})")
        if action == "wait":
            schedule.clear('waiting')

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
    waitjob = schedule.every(5).seconds.tag('waiting')
    print(waitjob)
    scheduler = SimpleScheduler()
    scheduler.addJob((waitjob,'wait'))
    scheduler.addCallback(jobCb)
    offJob = schedule.every().day.at(nowoff)
    print(offJob)
    scheduler.addJob((offJob, "off"))
    scheduler.addActionCallback("off", offCb)
    onJob = schedule.every().day.at(nowon)
    print(onJob)
    scheduler.addJob((onJob, "on"))
    scheduler.addActionCallback("on", onCb)
    scheduler.start()
    print(f"wait since {datetime.datetime.now()}")
    time.sleep(3*30)
    print(f"waiting is over at {datetime.datetime.now()}")
    scheduler.stop()
    print("done")

