from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from pathlib import Path
import xmltodict
import logging
import dateutil.parser as DateParser
import time
import threading, sys
from normalizeKeys import normalizeKeys
import json
from tzlocal import get_localzone
import copy

class RunTime:
    def __init__(self, parent = None):
        self._job = None
        self._parent = parent
        pass

    def __str__(self):
        return "<%s>" % (self.__class__.__name__)

    def createJob(self, name, backgroundScheduler):
        pass

    def jobCallback(self):
        logging.debug("%s.myJob: %s" % (self.__class__.__name__,self._job))
        if self._parent != None:
            self._parent.jobCallback(self._job)
            
class CronRunTime(RunTime):
    def __init__(self, parent, runtime):
        super().__init__(parent)
        if type(runtime) == dict:
            self.__init_constructor__(runtime)
        elif type(runtime) == CronRunTime:
            self.__copy_constructor__(runtime)
            
    def __init_constructor__(self, runtime):
        self._dayOfWeek = runtime['day_of_week']
        self._hour = runtime['hour']
        self._minute = runtime['minute']

    def __copy_constructor__(self, runtime):
        self._dayOfWeek = copy.deepcopy(runtime.dayOfWeek())
        self._hour = copy.deepCopy(runtime.hour())
        self._minute = copy.deepcopy(runtime.minute())
        
    def as_dict(self):
        return { 'day_of_week': self.dayOfWeek(), 'hour': self.hour(), 'minute': self.minute() }
    
    def __str__(self):
        return "<%s: dayOfWeek=%s, hour=%s, minute=%s>" % (self.__class__.__name__,self._dayOfWeek, self._hour, self._minute)

    def dayOfWeek(self):
        return self._dayOfWeek

    def hour(self):
        return self._hour

    def minute(self):
        return self._minute

    def createJob(self, name, baseScheduler):
        logging.debug("%s.createJob(self=%s,name=%s)" % (self.__class__.__name__, self.__str__(), name))

        self._job = baseScheduler.add_job(func = self.jobCallback, trigger='cron',
                                          name=name,
                                          day_of_week = self.dayOfWeek(),
                                          hour=self.hour(),
                                          minute=self.minute())
        
class DateRunTime(RunTime):
    def __init__(self, parent, runtime):
        super().__init__(parent)
        if type(runtime) == dict:
            self.__init_constructor__(runtime)
        elif type(runtime) == DateRunTime:
            self.__copy_constructor__(runtime)

    def __init_constructor__(self, runtime):
        logging.debug("%s.__init_constructor__(runtime=%s)" % (self.__class__.__name__, str(runtime)))

        self._date = DateParser.parse(runtime['date'])
        self._time = DateParser.parse(runtime['time']).time()

    def __copy_constructor__(self, runtime):
        self._date = copy.deepcopy(runtime.date())
        self._time = copy.deepcopy(runtime.time())

    def as_dict(self):
        return {'date': self.date(), 'time': self.time() }

    def __str__(self):
        return "<%s: date=%s, time=%s>" % (self.__class__.__name__,self.date(), self.time())

    def date(self):
        return self._date

    def time(self):
        return self._time

    def getDateTime(self):
        return datetime.datetime(self.date().year, self.date().month, self.date().day,
                        self.time().hour, self.time().minute, self.time().second)
    
    def createJob(self, name, baseScheduler):
        logging.debug("%s.createJob(self=%s,name=%s)" % (self.__class__.__name__, self.__str__(), name))
        self._job = baseScheduler.add_job(self.jobCallback, trigger='date',
                                          name = name,
                                          run_date = self.getDateTime())
        return self._job
    
class RadioJob:
    def __init__(self, parent, job=None):
        self._parent = parent
        if type(job) == dict:
            self.__init_constructor__(job)
        elif type(job) == RadioJob:
            self.__copy_constructor__(job)

    def __init_constructor__(self, job):
        self._name = job['name']
        self._active = job['active']
        self._type = job['type']
        self._runtime = self.createRunTime(job['runtime'])
        self._sender = job['sender'] if 'sender' in job else None
        print("__init_constructor__(sender=%s)" % (self.sender()))
        logging.debug("%s.__init_constructor__(runtime=%s)" % (self.__class__.__name__, str(self._runtime)))
        if "duration" in job:
            self._duration = eval(job['duration'])
        else:
            self._duration = 30

    def __copy_constructor__(self, job):
        self._name = copy.deepcopy(job.name())
        self._active = copy.deepcopy(job.active())
        self._type = copy.deepcopy(job.type())
        self._runtime = copy.deepcopy(job.runtime())
        self._sender = copy.deepcopy(job.sender())
        print("__copy_constructor(sender =", self.sender(),")")
        self._duration = copy.deepcopy(job.duration())
        
    def as_dict(self):
        return {'name': self.name(), 'type': self.type(), 'active': self.active(), 'runtime': self.runtime().as_dict(), 'sender': self.sender()}
    
    def createRunTime(self, runtime) -> RunTime:
        logging.debug("%s.createRunTime(runtime=%s)" % (self.__class__.__name__, str(runtime)))
        if self._type == 'cron':
            logging.debug("%s.createRunTime(): create CronRunTime" % (self.__class__.__name__))
            runtime = CronRunTime(self, runtime)
        else:
            logging.debug("%s.createRunTime(): create DateRunTime" % (self.__class__.__name__))
            runtime = DateRunTime(self,runtime)
            if runtime.getDateTime() < datetime.datetime.now():
                runtime = None            
        return runtime
    
    def name(self):
        return self._name

    def duration(self):
        return self._duration

    def set_active(self, value):
        self._active = value
        
    def set_name(self, name):
        self._name = name

    def set_type(self, value):
        self._type = value

    def set_runtime(self, value):
        self._runtime = value

    def set_duration(self, value):
        self._duration = value

    def set_sender(self, value):
        self._sender = value
        
    def active(self):
        return self._active

    def duration(self):
        return self._duration
    
    def sender(self):
        return self._sender
    
    def type(self):
        return self._type

    def runtime(self):
        return self._runtime

    def jobCallback(self, job):
        logging.debug("%s.jobCallback(job=%s)" % (self.__class__.__name__,str(job)))
        if self._parent != None:
            self._parent.jobCallback(self, job)
        
    def createJob(self, baseScheduler):
        if self.active() and self.runtime() != None:
            return self.runtime().createJob(self.name(),baseScheduler)
        return None
            
    def __str__(self):
        return "<%s: name=%s, active=%s, type=%s, runtime=%s, sender=%s>" % (self.__class__.__name__,
                                                                  self._name,
                                                                  self._active,
                                                                  self._type,
                                                                  self._runtime,
                                                                  self._sender)
    
class RadioScheduler:
    def __init__(self, configFile):
        self._readConfigFile(configFile)
        self._jobs = {}
        self._baseScheduler = BackgroundScheduler()
        self._addJobHandler = None
        self._jobHandler = None
        self._testing = False

    def set_testing(self, value = True):
        self._testing = value

    def testing(self):
        return self._testing
    
    def _readConfigFile(self, configFile):
        if Path(configFile).suffix == '.xml':
            self._readXmlConfigFile(configFile)
        elif Path(configFile).suffix == '.json':
            self._readJsonConfigFile(configFile)
        else:
            raise NotImplementedError()

    def _readJsonConfigFile(self, configFile):
        with open(configFile) as f:
            config = json.load(f)
            self._config = config['scheduler']['job']
        
    def _readXmlConfigFile(self, configFile):
        orig_config = xmltodict.parse(Path(configFile).read_text())
        config = normalizeKeys(orig_config)
        self._config = config['scheduler']['job']

    def createJob(self, job) -> RadioJob:
        return RadioJob(self, job)
    
    def createJobs(self):
        for job in self._config:
            radioJob = self.createJob(job)
            if radioJob != None:
                self._jobs[radioJob.name()] = radioJob

    def addJobs(self):
        logging.debug(">>>%s.addJobs()" % (self.__class__.__name__))
        for (name,job) in self._jobs.items():
            if not job.active():
                continue
            job.createJob(self._baseScheduler)
            if self._addJobHandler != None:
                self._addJobHandler(name, job)
                
    def jobCallback(self, radioJob, job):
        logging.debug("%s.jobCallback(radioJob= %s, job=%s)" % (self.__class__.__name__,str(radioJob),str(job)))
        if radioJob.name().startswith("start_") and radioJob.duration() == 0:
            return
        
        now = datetime.datetime.now()
        tz = get_localzone()
        later = (now + datetime.timedelta(0,0,0,0,radioJob.duration(),0)).replace(tzinfo=tz)
        
        nextRunTime = job.next_run_time.replace(tzinfo = tz)
        
        if radioJob.name().startswith("start_") and ((self.testing()) or (nextRunTime > later)):
            stopJob = RadioJob(self)
            stopJob.set_name(radioJob.name().replace("start_", "stop_"))
            stopJob.set_type('date')
            stopJob.set_active(True)
            date = str(later.date())
            time = str(later.time())
            logging.debug("%s.jobCallback(date=%s, time=%s)" % (self.__class__.__name__, date, time))
            stopJob.set_runtime(DateRunTime(stopJob,{'date': date, 'time': time }))
            stopJob.set_sender(None)
            stopJob.set_duration(0)
            logging.debug("%s.jobCallback(stopJob=%s)" % (self.__class__.__name__,stopJob))
            stopJob.createJob(self._baseScheduler)
            self._jobHandler(radioJob)
        else:
            print("%s.jobCallback(): job=%s" % (self.__class__.__name__, str(radioJob)))
            if radioJob.name().startswith("stop_"):
                print("%s.jobCallback(): call jobHandler to stop radio for job(%s)" % (self.__class__.__name__, str(radioJob)))
                self._jobHandler(radioJob)
            else:
                logging.debug("%s.jobCallback(): calling job is not a start job or next runtime (%s) is before stop time (%s)" % (self.__class__.__name__, nextRunTime, later))
        
    def nextJob(self):
        allJobs = self._baseScheduler.get_jobs()
        nextJob = None
        for job in allJobs:
            if (job.next_run_time == None):
                continue
            if (nextJob == None) or (job.next_run_time < nextJob.next_run_time):
                nextJob = job
        return nextJob

    def nextRunTime(self):
        nextJob = self.nextJob()
        if nextJob != None:
            return nextJob.next_run_time
        else:
            return None

    def getJob(self, name):
        if name in self._jobs:
            return self._jobs[name]
        else:
            return None

    def setAddJobHandler(self, handler):
        self._addJobHandler = handler
        
    def setJobHandler(self, handler):
        logging.debug("%s.setHandler()" % (self.__class__.__name__))
        self._jobHandler = handler
            
    def start(self):
        self.createJobs()
        self.addJobs()
        self._baseScheduler.start()

    def shutdown(self):
        self._baseScheduler.shutdown()
        
    def __str__(self):
        s = "<%s: jobs=[" % (self.__class__.__name__,)
        first = True
        for job in self._jobs:
            if not first:
                s+= ", "
            else:
                first = False
            s+= str(job)

        s+= "]>"
        return s

def foo(job):
    print("hello world %s" % str(job))
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    radioScheduler = RadioScheduler('waketime.json')
    radioScheduler.set_testing()
    print(str(radioScheduler))
    radioScheduler.setJobHandler(foo)
    radioScheduler.start()
    logging.debug("next run time: %s" % radioScheduler.nextRunTime())
    try:
        while True:
            print('.',end='')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        radioScheduler.shutdown()
##    scheduler = BackgroundScheduler()
##    scheduler.add_job(func=foo, trigger='cron', day_of_week="mon-fri", hour='*', minute="0,10,20,30,40")
##    scheduler.start()
    
