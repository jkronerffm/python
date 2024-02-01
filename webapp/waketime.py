import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj
from common.dictToObj import obj
import json
import logging

gridHtml="""
<!doctype html>
<html>
<head>
    <script type="text/javascript">
      function setActive(name) {
          const xhttp = new XMLHttpRequest();
          xhttp.onload = function() {
           };
          xhttp.open("GET", "/radio/waketime/set_active?name=" + name, true);
          xhttp.send();
      }
    </script>
    <meta name="viewport" content="width=device-width">
    <title>Weckzeiten</title>
</head>
<body>
    <h1>Weckzeiten</h1>
    <table>
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
          <td><input type="text" id="duration" name="duration" value="%s"/>
        </tr>
        <tr>
          <td><label for="sender">Sender:</label</td>
          <td><select id="sender" name="sender">
%s
          </select>
        </tr>
        <tr>
          <td colspan="2" style="align:center;">
            <input type="submit" value="Speichern"><input type="button" value="Zur&uuml;ck" onclick="location.assign('/radio/waketime/grid')"><input type="button" value="Delete" onclick="location.assign('/radio/waketime/delete?name=' + document.getElementById('name').value)">
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

def build_gridRow(job):
    indent = "    "
    rowIndent = 2*indent
    colIndent = 3*indent
    row=""
    runtime = build_runtime(job)
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
    editLink = f"/radio/waketime/edit?name={job.name}"
    row+= f"{rowIndent}<tr>\n"
    row+= f"{colIndent}<td><a href=\"{editLink}\">{content}</a></td>\n"
    row+= f"{colIndent}<td><input type=\"checkbox\" name=\"active\" {active} id=\"{job.name}\" onClick=\"setActive('{job.name}')\"/></td>\n"
    row+= f"{rowIndent}</tr>\n"
    return row

def build_grid():
    data = getData()
    content = ""
    for job in data.scheduler.job:
        content+= build_gridRow(job)
    return gridHtml % (content)

def build_formRow(job, name):
    pass

def build_edit(name):
    global data
    global radioSender

    if radioSender == None:
        radioSender = readData(filepathRadioSender)

    job = getJob(name)
    checked = "checked=\"checked\""
    dateChecked = checked if job.type=="date" else ""
    senderOptions = 12* " " + "<option value=""></option>"
    for sender in radioSender.sender:
        selected = "selected" if hasattr(job, 'sender') and job.sender == sender.name else ""
        senderOptions += 12*" " + f"<option value=\"{sender.name}\" {selected}>{sender.name}</option>\n"
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
        timecron = "%02d:%02d" % (int(job.runtime.hour), int(job.runtime.minute))
    sender = job.sender if hasattr(job, 'sender') else ""
    content += ("block" if job.type=="cron" else "none", timecron)
    content += (job.duration, senderOptions, day)
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

def save(name,theType, date, time, days_of_week, duration, sender):
    job = getJob(name)
    job.type = theType
    if theType == "date":
        job.runtime = dictToObj.obj({'date': date, 'time': time[0]})
    else:
        timestr = time[1].split(':')
        job.runtime = dictToObj.obj({'day_of_week': translate_daysOfWeek(days_of_week), 'hour': timestr[0], 'minute': timestr[1]})
    job.duration = duration
    job.sender = sender
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
}

def retranslate_daysOfWeek(daysOfWeek):
    daysOfWeekList = daysOfWeek.split(',')
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
    value = 0
    translation=""
    for day_of_week in daysOfWeek:
        value = value + daysValues[day_of_week]

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
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    for d in [['mon', 'tue', 'wed', 'thu', 'fri'], ['mon', 'tue', 'wed', 'fri', 'sat', 'sun'], ['mon', 'wed', 'fri'], ['mon','tue', 'wed', 'fri'], ['mon', 'tue', 'thu','fri','sat']]:
        translation = translate_daysOfWeek(d)
        logging.debug(f"in: {d}, out: {translation}")
    
    for d in ['mon-fri','mon,wed,thu-sat']:
        translation = retranslate_daysOfWeek(d)
        logging.debug(f"in: {d}, out: {translation}")
