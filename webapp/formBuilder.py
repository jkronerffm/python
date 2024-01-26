import dictToObj
from dictToObj import obj
import json
import logging

formTable="""
<html>
<head>
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

data = None

def readData(filepath):
    obj = None
    with open(filepath) as f:
        jsonStr = f.read()
        logging.debug(f"readData(filepath={filepath}) => jsonStr={jsonStr}")
        jsonData = json.loads(jsonStr)
        logging.debug(f"readData(filepath={filepath}) => jsonData={jsonStr}")
        o = dictToObj.obj(jsonData)
    return o

def build_runtime(job):
    runtime = job.runtime
    logging.debug(runtime)
    s = "%s %s:%s" % (runtime.day_of_week, "%02d" % (int(runtime.hour)) if runtime.hour != "*" else runtime.hour,"%02d" % (int(runtime.minute)) if runtime.minute != "*" else runtime.minute) if job.type == "cron" else f"{runtime.date} {runtime.time}"
    return s

def build_row(job):
    logging.debug(f"build_row(job={job})")
    indent = "    "
    rowIndent = 2*indent
    colIndent = 3*indent
    row=""
    runtime = build_runtime(job)
    duration = job.duration if hasattr(job, 'duration') else ''
    active = "checked=\"checked\"" if job.active else ""
    row+= f"{rowIndent}<tr>\n"
    row+= f"{colIndent}<td>{runtime}</td>\n"
    row+= f"{colIndent}<td>{duration}</td>\n"
    row+= f"{colIndent}<td><input type=\"checkbox\" name=\"active\" {active} id=\"{job.name}\"/></td>\n"
    row+= f"{rowIndent}</tr>\n"
    return row

def build_grid(computer):
    global data
    if data == None:
        data = readData(filepath = "/var/radio/conf/waketime.json")
    content = ""
    for job in data.scheduler.job:
        content+= build_row(job)
    return formTable % (content)

def getData(computer):
    global data
    return data

def getJob(name):
    global data

    for job in data.scheduler.job:
        if job.name == name:
            return job
    return None

def activateJob(name):
    global data

    job = getJob(name)
    job.active = not job.active

def writeData():
    global data
    jsonStr = dictToObj.objToJson(data)
    print(jsonStr)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    form = build_form()
    print(form)

    data = getData()
    print(data)

    activateJob("start_dauernd")
    print(data)

    writeData()
