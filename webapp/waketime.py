import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj
from common.dictToObj import obj
import json
import logging

gridHtml="""
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
    </table>
</body>
</html>
"""

formHtml="""
<html>
  <head>
    <meta name="viewport" content="width=device-width">
    <title>Bearbeite Weckzeit</title
  </head>
  <body>
    <form>
      <table>
        <tr colspan="2">
          <td><input type="checkbox" id="once" name="once" value="einmalig" %s><label for="once">einmalig</label></td>
        </tr>
        <tr colspan="2">
          <td>
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
                  <td> <input type="checkbox" id="day" name="day" value="1" >Montag</td>
                  <td> <input type="checkbox" id="day" name="day" value="2" >Dienstag</td> 
                  <td> <input type="checkbox" id="day" name="day" value="4" >Mittwoch</td> 
                </tr>
                <tr>
                  <td> <input type="checkbox" id="day" name="day" value="8" >Donnerstag</td>
                  <td> <input type="checkbox" id="day" name="day" value="16">Freitag</td> 
                  <td> <input type="checkbox" id="day" name="day" value="32">Dienstag</td>
                </tr>
                <tr>
                  <td> <input type="checkbox" id="day" name="day" value="64">Sonntag</td>
                </tr>
                <script type="text/javascript">
                  document.getElementById("day).value="%s";
                </script>
                <tr>
                  <td><label for="timecron">Zeit</label</td>
                  <td><input type="time" id="timecron" name="timecron" value="%s"></td>
                </tr>
              </table>
            </div>
          </td>
        </tr>
        <tr>
          <td>Dauer[Min]:</td>
          <td><input type="text" id="duration" value="%s"/>
        </tr>
        <tr>
          <td><label for="sender">Sender:</label</td>
          <td><select id="sender" name="sender" value="%s">
%s
          </select>
        </tr>
      </table>
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
    logging.debug(f"build_grid(<{type(data)}({dir(data)})>)")
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
    logging.debug(job)
    checked = "checked=\"checked\""
    dateChecked = checked if job.type=="date" else ""
    cronChecked = checked if job.type=="cron" else ""
    senderOptions = 12* " " + "<option value=""></option>"
    for sender in radioSender.sender:
        senderOptions += 12*" " + f"<option value=\"{sender.name}\">{sender.name}</option>\n"
    content = (dateChecked, )
    if job.type == "date":
        date = job.runtime.date
        time = job.runtime.time
        
    content+= ("block" if job.type=="date" else "none", date, time)
    day = ""
    timecron = ""
    if job.type == "cron":
        if job.runtime.day_of_week == "Mon-Fri":
            day = "1,2,4,8,16"
        timecron = "%02d:%02d" % (job.runtime.hour, job.runtime.minute)
    content += ("block" if job.type=="date" else "none", day, timecron)
    content += (job.duration, job.sender, senderOptions)
    logging.debug(f"len(content)={len(content)}")
    logging.debug(f"s.count(%s)={formHtml.count('%s')}")
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
    
    logging.debug(f"getJob(data={data})")
    
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
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    grid = build_grid()
    print(grid)

    job = getJob("start_once")
    print(job)
    
    edit = build_edit("start_once")
    print(edit)
