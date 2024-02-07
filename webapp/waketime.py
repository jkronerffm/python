import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj
from common.dictToObj import obj
import json
import uuid
import logging
from datetime import datetime

gridHtml="""
<!doctype html>
<html>
<head>
    <style>
      .waketimerow {
        cursor: pointer;        
      }

      .waketimerow:hover {
        box-shadow: 2px 2px 2px 2px;
      }
    </style>
    <script type="text/javascript">
      function setActive(name) {
          const xhttp = new XMLHttpRequest();
          xhttp.onload = function() {
           };
          xhttp.open("GET", "/radio/waketime/set_active?name=" + name, true);
          xhttp.send();
      }

      function editJob(name) {
        window.location.replace("/radio/waketime/edit?name="+name);
      }
    </script>
    <meta name="viewport" content="width=device-width">
    <title>Weckzeiten</title>
</head>
<body>
    <h1>Weckzeiten</h1>
    <table>
      <tr>
        <th>Tag</th>
        <th>Zeit</th>
        <th>Dauer[Min]</td>
        <th>Sender</th>
        <th>Aktiv</th>
      </tr>
%s
      <tr>
        <td colspan="2">
          <input type="button" value="+" onclick="location.assign('/radio/waketime/add')"><input type="button" value="Zur&uuml;ck" onclick="location.assign('/')">
        </td>
      </tr>
    </table>
</body>
</html>
"""

formHtml="""
<html>
  <head>
    <meta name="viewport" content="width=device-width">
    <title>Bearbeite Weckzeit</title>
    <script type="text/javascript">
      function switchRuntime(dateOrCron) {
        var div1 = document.getElementById('runtime_once');
        var div2 = document.getElementById('runtime_repeatedly');
        if (dateOrCron.checked) {
            div1.style.display="block";
            div2.style.display="none";
        } else {
            div1.style.display="none";
            div2.style.display="block";
        }
      }
    </script>
  </head>
  <body>
    <form method="get" action="/radio/waketime/save">
      <input type="hidden" id="name" name="name", value="%s">
      <table>
        <tr>
          <td  colspan="2"><input type="checkbox" id="dateOrCron" name="dateOrCron" value="date"  onClick="switchRuntime(this)" %s><label for="dateOrCron">einmalig</label></td>
        </tr>
        <tr>
          <td colspan="2">
            <div id="runtime_once" style="display: %s;">
              <table>
                <tr>
                  <td>
                    Datum:
                  </td>
                  <td>
                    <input type="date" id="date" name="date" value="%s">
                  </td>
                </tr>
                <tr>
                  <td>
                    Zeit:
                  </td>
                  <td>
                    <input type="time" id="time" name="time" value="%s">
                  </td>
                </tr>
              </table>
            </div>
            <div id="runtime_repeatedly" style="display: %s;">
              <table>
                <tr>
                  <td> <input type="checkbox" id="mon" name="day_of_week" value="mon" >Montag</td>
                  <td> <input type="checkbox" id="tue" name="day_of_week" value="tue" >Dienstag</td> 
                  <td> <input type="checkbox" id="wed" name="day_of_week" value="wed" >Mittwoch</td> 
                </tr>
                <tr>
                  <td> <input type="checkbox" id="thu" name="day_of_week" value="thu" >Donnerstag</td>
                  <td> <input type="checkbox" id="fri" name="day_of_week" value="fri">Freitag</td> 
                  <td> <input type="checkbox" id="sat" name="day_of_week" value="sat">Samstag</td>
                </tr>
                <tr>
                  <td> <input type="checkbox" id="sun" name="day_of_week" value="sun">Sonntag</td>
                </tr>
                <tr>
                  <td><label for="timecron">Zeit</label</td>
                  <td><input type="time" id="time" name="time" value="%s"></td>
                </tr>
              </table>
            </div>
          </td>
        </tr>
        <tr colspan="2">
          <td>Dauer[Min]:</td>
          <td><input type="number" min="0" max="59" id="duration" name="duration" value="%s"/>
        </tr>
        <tr>
          <td><label for="sender">Sender:</label</td>
          <td><select id="sender" name="sender">
%s
          </select>
        </tr>
        <tr>
          <td colspan="5" style="align:center;">
            <input type="submit" value="Speichern"><input type="button" value="Zur&uuml;ck" onclick="location.assign('/radio/waketime/grid')"><input type="button" value="-" onclick="location.assign('/radio/waketime/delete?name=' + document.getElementById('name').value)">
          </td>
        </tr>
      </table>
      <script type="text/javascript">
        var checkedDays = "%s".split(",");
        var checkBoxes = document.getElementsByName("day_of_week");
        for (var i = 0; i < checkBoxes.length; i++) {
          if (checkedDays.indexOf(checkBoxes[i].value) !== -1) {
            checkBoxes[i].checked = true;
          }
        }
      </script>
    </form>
  </body>
</html>
"""

data = None
radioSender = None
filepath = "/var/radio/conf/waketime.json"
filepathRadioSender = "/var/radio/conf/radio.json"

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
        s = "%s" % (translate_days(runtime.day_of_week, mainLanguage))
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

def build_gridRow(job, mainLanguage):
    indent = "    "
    rowIndent = 2*indent
    colIndent = 3*indent
    row=""
    runtime = build_runtime(job)
    runtimeDay = build_runtimeDay(job, mainLanguage)
    runtimeTime = build_runtimeTime(job)
    if hasattr(job, 'duration'):
        duration = f", Dauer:{str(job.duration)}Min."
    else:
        duration = ""
    if hasattr(job, 'sender'):
        sender = f",Sender: {job.sender}"
    else:
        sender = ''
    
    active = "checked=\"checked\"" if job.active else ""
    content = runtime + duration + sender
##    editLink = f"/radio/waketime/edit?name={job.name}"
    row += f"{rowIndent}<tr class=\"waketimerow\">\n"
    row += f"{colIndent}<td onclick=\"editJob('{job.name}')\">{runtimeDay}</td>\n"
    row += f"{colIndent}<td onclick=\"editJob('{job.name}')\">{runtimeTime}</td>\n"
    row += f"{colIndent}<td style=\"text-align:right\" onclick=\"editJob('{job.name}')\">{str(job.duration)}</td>\n"
    row += f"{colIndent}<td onclick=\"editJob('{job.name}')\">{job.sender}</td>\n"
##    row+= f"{rowIndent}<tr>\n"
##    row+= f"{colIndent}<td><a href=\"{editLink}\">{content}</a></td>\n"
    row+= f"{colIndent}<td><input type=\"checkbox\" name=\"active\" {active} id=\"{job.name}\" onClick=\"setActive('{job.name}')\"/></td>\n"
    row+= f"{rowIndent}</tr>\n"
    return row

def build_grid(mainLanguage):
    data = getData()
    content = ""
    for job in data.scheduler.job:
        content+= build_gridRow(job,  mainLanguage)
    return gridHtml % (content)

def build_edit(name):
    global data
    global radioSender

    if radioSender == None:
        radioSender = readData(filepathRadioSender)

    job = getJob(name)
    senderOptions = 12* " " + "<option value=""></option>"
    for sender in radioSender.sender:
        selected = "selected" if job != None and hasattr(job, 'sender') and job.sender == sender.name else ""
        senderOptions += 12*" " + f"<option value=\"{sender.name}\" {selected}>{sender.name}</option>\n"
    if job != None:
        checked = "checked=\"checked\""
        dateChecked = checked if job.type=="date" else ""
        content = (name, dateChecked, )
        if job.type == "date":
            date = job.runtime.date
            time = job.runtime.time
        else:
            date=""
            time=""
            
        content+= ("block" if job.type=="date" else "none", date, time)
        day = ""
        timecron = ""
        if job.type == "cron":
            day = retranslate_daysOfWeek(job.runtime.day_of_week)
            hour = "%02d" % (int(job.runtime.hour)) if job.runtime.hour != '*' else ''
            minute = "%02d" % (int(job.runtime.minute)) if job.runtime.minute != '*' else ''
            timecron = "%s:%s" % (hour, minute)
        sender = job.sender if hasattr(job, 'sender') else ""
        duration = job.duration if hasattr(job, 'duration') else ""
        content += ("block" if job.type=="cron" else "none", timecron)
        content += (duration, senderOptions, day)
    else:
        content = (name, "", "none", "", "", "block", "", "", senderOptions, "")
    html = formHtml % content
    return html

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
        
def createJob(name,theType, date, time, days_of_week, duration, sender):
    data = getData()
    jobDict = {
        'name': name,
        'type': theType,
        'duration': duration,
        'sender': sender,
        'runtime': createRuntime(theType, date, time, days_of_week),
        'active': False
    }
    data.scheduler.job.append(dictToObj.obj(jobDict))
    
def save(name,theType, date, time, days_of_week, duration, sender):
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
    else:
        createJob(name, theType, date, time, days_of_week, duration, sender)
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
    logging.debug(f"translate_days(daysOfWeek={daysOfWeek}, targetLanguage={targetLanguage})")
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
    logging.debug(f"translate_daysOfWeek(daysOfWeek={daysOfWeek})")
    if not(daysOfWeek) is list:
        return daysOfWeek
    value = 0
    translation=""
    for day_of_week in daysOfWeek:
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
    return build_edit(name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    (h,m) = splitTimeString('12:10')
    logging.debug(f"h={h}, m={m}")
    (h,m) = splitTimeString('*:*')
    logging.debug(f"h={h}, m={m}")
    (h,m) = splitTimeString('*:10')
    logging.debug(f"h={h}, m={m}")
    (h,m) = splitTimeString('12:*')
    logging.debug(f"h={h}, m={m}")

    r = createRuntime('date', '01.02.2024', ['12:10', ''], '')
    logging.debug(f"runtime = {str(r)}")
    r = createRuntime('cron', '', ['', ''], '*')
    logging.debug(f"runtime = {str(r)}")
    r = createRuntime('cron', '', ['', '12:30'], 'mon-wed,fri-sun')
    logging.debug(f"runtime = {str(r)}")

    createJob('blah1', 'date','01.02.2024', ['13:00', ''], '', '10', 'hr1')
    data = getData()
    logging.debug(f"data={str(data)}")

    createJob('blah2', 'cron','', ['','13:00'], 'tue,thu,fri-sun', '10', 'hr3')
    data = getData()
    logging.debug(f"data={str(data)}")

    job = getJob('blah1')
    s = build_runtimeDay(job)
    logging.debug(s)
    job = getJob('blah2')
    s = build_runtimeTime(job)
    logging.debug(s)

    for days in ['mon', 'mon,wed,fri', 'mon-wed,fri', 'mon-wed,fri-sun']:
        for lang in ['en', 'de', 'es']:
            translatedDays = translate_days(days, lang)
            logging.debug(f"target language={lang}, input={days}, output={translatedDays}")
