import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj
from common.dictToObj import obj
import json
import uuid
import logging
from datetime import datetime


data = None
radioSender = None
confPath = "/var/radio/conf"
filepath = f"{confPath}/waketime.json"
filepathRadioSender = f"{confPath}/radio.json"

def readData(filepath):
    obj = None
    with open(filepath) as f:
        jsonStr = f.read()
        jsonData = json.loads(jsonStr)
        obj = dictToObj.obj(jsonData)
        f.close()
    return obj

def build_runtime(job):
    runtime = job.runtime
    s = "%s %s:%s" % (runtime.day_of_week, "%02d" % (int(runtime.hour)) if runtime.hour != "*" else runtime.hour,"%02d" % (int(runtime.minute)) if runtime.minute != "*" else runtime.minute) if job.type == "cron" else f"{runtime.date} {runtime.time}"
    return s

def build_runtimeDay(job, mainLanguage):
    runtime = job.runtime
    if job.type == "cron":
        s = "%s" % (translate_days(translate_daysOfWeek(runtime.day_of_week), mainLanguage))
    else:
        dt = datetime.strptime(runtime.date, '%Y-%m-%d')
        s = dt.strftime('%d.%m.%Y')
        
    return s

def build_runtimeTime(job):
    logging.debug(f"build_runtimeTime(job={str(job)})")
    runtime = job.runtime
    if job.type == "cron":
        hour = "%02d" % (int(runtime.hour)) if type(runtime.hour) is int else runtime.hour
        minute = "%02d" % (int(runtime.minute)) if type(runtime.minute) else runtime.minute
        
        s = "%s:%s" % (hour, minute)
    else:
        s = job.runtime.time
    return s

def createJobRow(job, mainLanguage):
    runtime = build_runtime(job)
    runtimeDay = build_runtimeDay(job, mainLanguage)
    runtimeTime = build_runtimeTime(job)
    jobRow = {
        'name': job.name,
        'runtimeDay': runtimeDay,
        'runtimeTime': runtimeTime,
        'duration': job.duration,
        'sender': job.sender,
        'timeannouncement': 'Ja' if hasattr(job, 'timeannouncement') and job.timeannouncement else 'Nein',
        'active': "checked=\"checked\"" if job.active else ""
    }
    return jobRow

def createJobList(mainLanguage):
    data = getData()
    jobList = []
    for job in data.scheduler.job:
        jobRow = createJobRow(job, mainLanguage)
        jobList.append(jobRow)
    return jobList

def getHeaderList(mainLanguage):
    return ["Tag", "Zeit", "Dauer [Min]", "Sender", "Zeitansage", "Aktiv"]

def getSenderList(job):
    global radioSender

    if radioSender == None:
        radioSender = readData(filepathRadioSender)
        
    senderList = []
    for sender in radioSender.sender:
        item = {
            'name': sender.name,
            'selected': 'selected' if job != None and sender.name == job.sender else ''
        }
        senderList.append(item)
    return senderList

def createEdit(name):
    job = getJob(name)
    senderList = getSenderList(job)
    if job != None:
        if job.type == 'cron':
            hour = "%02d" % (int(job.runtime.hour)) if job.runtime.hour != '*' else ''
            minute = "%02d" % (int(job.runtime.minute)) if job.runtime.minute != '*' else ''
            timecron = "%s:%s" % (hour, minute)
        else:
            timecron = ""
        editJob = {
           'name': job.name,
           'type': 'checked="checked"' if job.type == 'date' else '',
           'displayDate': "block" if job.type=='date' else 'none',
           'date': job.runtime.date if job.type=='date' else '',
           'datetime': job.runtime.time if job.type=='date' else '',
           'displaycron': "block" if job.type=='cron' else 'none',
           'crontime': timecron,
           'duration': job.duration if hasattr(job, 'duration') else "",
           'sender': job.sender if hasattr(job, 'sender') else "",
           'daysOfWeek': retranslate_daysOfWeek(job.runtime.day_of_week) if hasattr(job.runtime, 'day_of_week') else '',
           'timeannouncement': job.timeannouncement if hasattr(job, 'timeannouncement') else ''
        }
    else:
        editJob = {
            'name': name,
            'type': '',
            'displayDate': 'none',
            'date': '',
            'datetime': '',
            'displaycron': 'block',
            'crontime': '',
            'duration': '',
            'sender': '',
            'daysOfWeek': '',
            'timeannouncement': ''
        }
    return (senderList, editJob)
        
def getData():
    global data
    if data == None:
        data = readData(filepath)
        
    return data

def getJob(name):
    global data

    data = getData()
    
    for job in data.scheduler.job:
        if job.name == name:
            return job
    return None

def new_name():
    name = "start_"
    uniqueName =  str(uuid.uuid4())
    name += uniqueName
    return  name

def activateJob(name):
    global data

    job = getJob(name)
    job.active = not job.active
    return job.active

def writeData():
    global data
    global filepath
    jsonStr = dictToObj.objToJson(data)
    with open(filepath, 'w') as f:
        f.write(jsonStr)
        f.close()

def getNumeric(val):
    return int(val) if val.isnumeric() else val

def splitTimeString(time):
    timeval = time.split(':') if len(time) > 0 else ['*', '*']
    return (getNumeric(timeval[0]), getNumeric(timeval[1]))

def createRuntime(theType, date, time, days_of_week):
    (h, m) = splitTimeString(time[1])
    dictRuntime = { 'date': date, 'time': time[0] } if theType == 'date' else { 'day_of_week': translate_daysOfWeek(days_of_week), 'hour': h, 'minute': m }
    return dictToObj.obj(dictRuntime)
        
def createJob(name,theType, date, time, days_of_week, duration, sender, timeAnnouncement):
    data = getData()
    jobDict = {
        'name': name,
        'type': theType,
        'duration': duration,
        'sender': sender,
        'runtime': createRuntime(theType, date, time, days_of_week),
        'timeannouncement': timeAnnouncement,
        'active': False
    }
    data.scheduler.job.append(dictToObj.obj(jobDict))
    
def save(name,theType, date, time, days_of_week, duration, sender, timeAnnouncement):
    job = getJob(name)
    if job != None:
        job.type = theType
        if theType == "date":
            job.runtime = dictToObj.obj({'date': date, 'time': time[0]})
        else:
            timestr = time[1].split(':') if len(time[1]) > 0 else ['*','*']
            job.runtime = dictToObj.obj({'day_of_week': retranslate_daysOfWeek(days_of_week), 'hour': timestr[0], 'minute': timestr[1]})
        job.duration = duration
        job.sender = sender
        setattr(job, 'timeannouncement', timeAnnouncement)
    else:
        createJob(name, theType, date, time, days_of_week, duration, sender, timeAnnouncement)
    writeData()

daysValues = {
    'mon': 1,
    'tue': 2,
    'wed': 4,
    'mon-wed':7,
    'thu': 8,
    'tue-thu':14,
    'mon-thu':15,
    'fri': 16,
    'wed-fri':28,
    'tue-fri':30,
    'mon-fri':31,
    'sat': 32,
    'thu-sat':56,
    'wed-sat':60,
    'tue-sat':62,
    'mon-sat':63,
    'sun': 64,
    'thu-sun':104,
    'fri-sun':112,
    'wed-sun':124,
    'tue-sun':126,
    'mon-sun':127,
    '*':127
}

day_translation = {
    'de': {
        'mon': 'Mo',
        'tue': 'Di',
        'wed': 'Mi',
        'thu': 'Do',
        'fri': 'Fr',
        'sat': 'Sa',
        'sun': 'So'
    },
    'es': {
        'mon': 'lun',
        'tue': 'mar',
        'wed': 'mie',
        'thu': 'jue',
        'fri': 'vie',
        'sat': 'sab',
        'sun': 'dom'
    }
}

def translate_days(daysOfWeek, targetLanguage):
    if not (targetLanguage in day_translation.keys()):
        return daysOfWeek
    result = ""
    if ',' in daysOfWeek:
        l = daysOfWeek.split(',')
        for e in l:
            s = translate_days(e, targetLanguage)
            result += "," + s if len(result) > 0 else s
    elif '-' in daysOfWeek:
        l = daysOfWeek.split('-')
        for e in l:
            s = translate_days(e, targetLanguage)
            result += "-" + s if len(result) > 0 else s
    else:
        result = day_translation[targetLanguage][daysOfWeek]

    return result
    
def retranslate_daysOfWeek(daysOfWeek):
    daysOfWeekList = daysOfWeek if isinstance(daysOfWeek, list) else daysOfWeek.split(',')
    value = 0
    for d in daysOfWeekList:
        v = daysValues[d]
        value |= v

    translation = []
    for b in range(7):
        v = 1 << b
        if (value & v) > 0:
            translation.append(list(daysValues.keys())[list(daysValues.values()).index(v)])
    return ",".join(translation)
        
def translate_daysOfWeek(daysOfWeek):
    listOfDaysOfWeek = daysOfWeek if type(daysOfWeek) is list else daysOfWeek.split(",")

    value = 0
    translation=""
    for day_of_week in listOfDaysOfWeek:
        value = value + daysValues[day_of_week]

    if value == 127:
        return '*'
    values = list(daysValues.values())
    values.sort(reverse=True)
    for v in values:
        if (v & value) == v:
            key = list(daysValues.keys())[list(daysValues.values()).index(v)]
            sep = "," if len(translation) > 0 else ""
            translation = key + sep + translation
            value = value & ~v
    return translation

def delete(name):
    data = getData()
    data.scheduler.job = list(filter(lambda x: x.name != name, data.scheduler.job))
    writeData()

def add():
    name = new_name()
    return createEdit(name)

def clone(name):
    senderList, job = createEdit(name)
    logging.debug(f"clone(name={name}, job={job})")
    job['name'] = new_name()
    return (senderList, job)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dow = translate_daysOfWeek("mon,tue,wed")
    logging.debug(f"translate_daysOfWeek returned {dow}")
    dow = translate_daysOfWeek(["mon", "tue", "wed"])
    logging.debug(f"translate_daysOfWeek returned {dow}")
    days = translate_days('mon-wed', 'de')
    logging.debug(f"translate_days returned {days}")
    job = getJob('start_workday_halfpastfive')
    logging.debug(job)
    t = build_runtimeDay(job, 'de')
    logging.debug(f"build_runtimeDay({job}) returned {t})")
    (senderList, job) = clone(job.name)
    print(senderList)
    print(job)
