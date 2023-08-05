from apscheduler.schedulers.background import BackgroundScheduler
import gtts, playsound, os
import xmltodict, pathlib, datetime
import dateutil.parser as DateParser
import logging, inspect, uuid
import vlc

logger = logging.getLogger("remindMe")

class JobNotActiveError(Exception):
    "The job is not active"
    pass

class InvalidDateError(Exception):
    "The job's date is before now"
    pass

class RemindMeFileNotDefined(Exception):
    "The file remindMe.xml is not defined."
    pass

class AttributeNotFoundInDocumentError(Exception):
    "The requested attribute was not found in document."
    pass

class Reminder:
    def __init__(self, remindMeFile):
        self._remindMeFile = remindMeFile

        self._doc = None
        self._scheduler = BackgroundScheduler()
        self._lang="de"
        self._instance = vlc.Instance()
        self.readRemindMeFile()
        

    def __str__(self):
        return str(self._doc)
    
    def readRemindMeFile(self):
        if self._remindMeFile == None:
            raise RemindMeFileNotDefined()

        self._doc = xmltodict.parse(pathlib.Path(self._remindMeFile).read_text())

    def doc(self):
        return self._doc

    def reminder(self):
        return self.doc()['reminder']

    def _attributeByName(self, name, element = None, defaultValue = None) -> str:
        attrName = '@%s' % name
        if element == None:
            element = self.reminder()
        if attrName in element:
            return element[attrName]
        else:
            return defaultValue
            
    def _elementsByName(self, name):
        if name in self.reminder():
            return self.reminder()[name]
        else:
            return []
        
    def priorNotice(self) -> int:
        value = self._attributeByName('priorNotice')
        if value == None:
            return 0
        else:
            return int(value)
        
    def jobs(self):
        return self._elementsByName('job')
    
    def appointments(self):
        return self._elementsByName('appointment')

    def play(self, filepath, usePlaysound = False):
        if usePlaysound:
            playsound.playsound(filepath)
        else:
            logger.debug("(filepath=%s)"%(filepath))
            medialist = self._instance.media_list_new()
            uri = pathlib.Path(filepath).as_uri()
            media = self._instance.media_new(uri)
            medialist.add_media(media)
            player = self._instance.media_list_player_new()
            player.set_media_list(medialist)
            player.play()
    
    def say(self, text, usePlaysound = True):
        logger.debug("(text=%s)" % (text))
        tts = gtts.gTTS(text, lang=self.language())
        filename = str(uuid.uuid4()) + ".mp3"
        filepath = os.path.join("/tmp", filename)
        tts.save(filepath)
        self.play(filepath, usePlaysound)
        os.remove(filepath)
        
    def jobExecutor(self, text):
        logger.debug("(text=%s)" % (text))
        now = datetime.datetime.now()
        time = now.strftime("%H:%M")
        fulltext = "Jetzt ist es %s. %s" % (time, text)
        self.say(fulltext)
        
    def language(self):
        return self.reminder()["@lang"]
    
    def createCronJob(self, job):
        logger.debug("(job=%s)"%(str(job)))
        name = job['@name']
        dayOfWeek = job['@daysOfWeek']
        hour = job['@hour']
        minute = job['@minute']
        item = job['item']
        text = item["@text"]
        self._scheduler.add_job(self.jobExecutor, 'cron', name=name,
                                day_of_week=dayOfWeek, hour=hour, minute=minute,
                                kwargs={'text': text})

    def createDateJob(self, job):
        name = job['@name']
        date = job['@date']
        item = job['item']
        text = item['@text']
        runDate = DateParser.parse(date)
        now = datetime.datetime.now()
        logger.debug("(runDate=%s, now=%s)" % (runDate, now))
        if runDate < now:
            raise InvalidDateError()
        self._scheduler.add_job(self.jobExecutor, 'date', name=name,
                                run_date=DateParser.parse(date),
                                kwargs={'text':text})

    @staticmethod
    def IsActive(job, defActive=True):
        logger.debug("(job=%s, defActive=%s)" % (str(job), str(defActive)))
        if "@active" in job:
            active = eval(job["@active"])
        else:
            active = defActive
        logger.debug("active=%s" % (str(active)))
        return active
        
    def createScheduleJob(self, job):
        if not('@type' in job):
            raise AttributeNotFoundInDocumentError()
        jobType = job['@type']
        active = Reminder.IsActive(job)
        logger.debug("(active=%s)" % (str(active)))
        if not active:
            raise JobNotActiveError()
        logger.debug("(job=%s)"%(str(job)))
        if jobType == 'cron':
            self.createCronJob(job)
        elif jobType == 'date':
            self.createDateJob(job)

    def createScheduleJobsItself(self):
        for job in self.jobs():
            try:
                self.createScheduleJob(job)
            except JobNotActiveError:
                logger.warning("The job is not active.")
            except InvalidDateError:
                logger.warning("The requested date is before now.")                                    
            except Exception as e:
                logger.error("caught exception %s" % (str(e)))

    def getPriorNoticeTime(self, hour=None, minute=None, date=None):
        if self.priorNotice() > 0:
            if hour != None and minute != None:
                if minute > self.priorNotice():
                    m = minute - self.priorNotice()
                    h = hour
                else:
                    m = (minute + 60) - self.priorNotice()
                    if hour > 0:
                        h = hour - 1
                    else:
                        h = 23
                return (h, m)
            elif date != None:
                priorNoticeTime = date - datetime.timedelta(minutes=self.priorNotice())
                return priorNoticeTime
        else:
            return (None, None)
        
    def createCronJobFromAppointment(self,appointmentId,when, what):
        logger.debug("(apointmentId=%d, when=%s, what=%s)" % (appointmentId, when, what))
        every=when['@every']
        at=when['@at']
        if every == 'weekday':
            dayOfWeek = 'mon-fri'
        else:
            dayOfWeek = every
        appTime = DateParser.parse(at).time()
        hour = appTime.hour
        minute = appTime.minute
        logger.debug("() add cron job for %s at hour=%d, minute=%d" % (dayOfWeek, hour, minute))
        self._scheduler.add_job(self.jobExecutor, trigger='cron', name='job%d' % appointmentId,
                                day_of_week=dayOfWeek, hour=hour, minute=minute,
                                kwargs={'text': what})
        (h, m) = self.getPriorNoticeTime(hour=hour, minute=minute)
        if h == None or m == None:
            return
        logging.debug("() priorNoticeTime: hour=%d, minute=%d" % (h, m))
        self._scheduler.add_job(self.jobExecutor, trigger='cron', name='jobprior%d' % appointmentId,
                                day_of_week=dayOfWeek, hour=h,  minute=m,
                                kwargs={'text': what})

    def createDateJobFromAppointment(self,appointmentId, when, what):
        logger.debug("(appointmentId=%d, when=%s, what=%s)" % (appointmentId, when, what))
        on=when['@on']
        at=when['@at']
        onDate = DateParser.parse(on).date()
        atTime = DateParser.parse(at).time()
        date = datetime.datetime.combine(onDate,atTime)
        logger.debug('() add job at %s' % (str(date)))
        self._scheduler.add_job(self.jobExecutor, trigger='date', name='job%d' % appointmentId,
                                run_date=date, kwargs= { 'text' : what })
        priorNoticeDate = self.getPriorNoticeTime(date=date)
        logger.debug('() add prior job at %s' % (str(priorNoticeDate)))
        self._scheduler.add_job(self.jobExecutor, trigger='date', name='job%d' % appointmentId,
                                run_date=priorNoticeDate, kwargs= { 'text' : what })
    
    def createScheduleJobsByAppointments(self):
        logger.debug("()")
        for appointment in self.appointments():
            logger.debug("(appointment=%s)" % appointment)
            appointmentId = eval(appointment['@id'])
            when = appointment['when']
            what = appointment['what']
            if '@every' in when:
                self.createCronJobFromAppointment(appointmentId,when, what)
            elif '@on' in when:
                self.createDateJobFromAppointment(appointmentId, when, what)
                
    def createScheduleJobs(self):
        self.createScheduleJobsItself()
        self.createScheduleJobsByAppointments()
        self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown()

class NoTTSFilter(logging.Filter):
    def filter(self, record):
        return not record.name == "gtts.tts"
    
if __name__ == "__main__":
    logger.addFilter(NoTTSFilter())
    logging.getLogger('gtts.tts').addFilter(NoTTSFilter())
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s%(message)s')
    
    reminder = Reminder("remindMe.xml")
    logging.debug(reminder)
    reminder.createScheduleJobs()
