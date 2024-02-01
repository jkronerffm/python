from flask import Flask, redirect, request
import sys
sys.path.append("/home/jkroner/Documents/python")
import waketime
import logging

app = Flask(__name__)

htmlString ="""
<html>
  <head>
    <meta name="viewport" content="width=device-width"/>
    <title>Radio Einstellungen</title>
  </head>
  <body>
    <h1>Radio Einstellungen</h1>
    <table>
      <tr>
        <td> <input type="button" id="sender" value="Sender" onClick="location.assign('/radio/sender')"/> </td>
      </tr>
      <tr>
        <td> <input type="button" id="waketime" value="Weckzeiten" onClick="location.assign('/radio/waketime')"/> </td>
      </tr>
    </table>
  </body>
</html>
"""

@app.route("/")
@app.route("/radio")
def init():
    return htmlString

@app.route("/radio/waketime/")
def doWaketime():
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/grid")
def grid():
    return waketime.build_grid()

@app.route("/radio/waketime/set_active")
def set_active():
    name = request.args.get('name', default='', type=str)
    logging.debug(f"set_active({name})")
    waketime.activateJob(name)
    jsonData = waketime.writeData()
    return "name was set to active"

@app.route("/radio/waketime/edit")
def doEditWaketime():
    name=request.args.get('name', default='', type=str)
    return waketime.build_edit(name)

@app.route("/radio/waketime/save")
def doSaveWaketime():
    logging.debug(f"doSaveWaketime({request.args})")
    name = request.args.get('name', '')
    date = request.args.get('date', '')
    time = request.args.getlist('time')
    daysOfWeek=request.args.getlist('day_of_week')
    logging.debug(f">> daysOfWeek={daysOfWeek}")
    duration = request.args.get('duration', '1')
    sender = request.args.get('sender', '')
    theType= request.args.get('dateOrCron', "cron")
    waketime.save(name, theType, date, time, daysOfWeek, duration, sender)
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/delete")
def doDeleteWaketime():
    logging.debug(f"doDeleteWaketime({request.args})")
    name=request.args.get('name', '')
    if name != '':
        waketime.delete(name)
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/add")
def doAddWaketime():
    logging.debug("doAddWaketime")
    return waketime.add()


if __name__ == "main":
    logging.basicConfig(level="DEBUG")

    
