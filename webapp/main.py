import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from flask import Flask, redirect, request, render_template
import waketime
import logging
from common import dictToObj
import base64
from urllib.request import url2pathname
from urllib.parse import urlparse

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

def getLanguageList(acceptLanguages:str):
    result = []
    langs = acceptLanguages.split(',')
    for lang_quality_pair in langs:
        if ';' in lang_quality_pair:
            lang, quality = lang_quality_pair.split(';')
            quality = float(quality[2:])
        else:
            lang = lang_quality_pair
            quality = 1.0
        result.append({
            'code': lang.split('-')[0],
            'code-with-country': lang,
            'quality': quality
        })

        result.sort(key=lambda x: x['quality'], reverse=True)
    return result

def getMainLanguage(acceptLanguages:str):
    languageList = getLanguageList(acceptLanguages)
    return languageList[0]['code']

def loadImageToBase64(url):
    p = urlparse(url)
    filepath = url2pathname(p.path)
    ext = os.path.splitext(filepath)[1][1:]
    with open(filepath, "rb") as image_file:
        data = image_file.read()
        encoded_string = base64.b64encode(data).decode("utf-8")
        image_file.close()
        if ext == "svg":
            image_type = "svg+xml"
        else:
            image_type = ext
    image = f"data:image/{image_type};base64,{encoded_string}"
    return image

@app.route("/radio/sender/")
def doRadioSender():
    o = dictToObj.objFromJson("/var/radio/conf/radio.json")
    senderList = o.sender
    imageList = []
    for sender in senderList:
        image = loadImageToBase64(sender.image)
        imageList.append(image)
    return render_template("radio.html", title="Radio Sender", header="Radio Sender", headerlist=["Name", "Adresse", "Bild"],senderList = senderList, imageList = imageList)

@app.route("/radio/sender/edit")
def doEditSender():
    name = request.args.get("name")    
    o = dictToObj.objFromJson("/var/radio/conf/radio.json")
    sender = [x for x in o.sender if x.name == name]
    if len(sender) > 0:
        sender = sender[0]
    else:
        return redirect("/radio/sender")
    logging.debug(f"doSenderEdit(name={name},sender={sender})")
    imageData=loadImageToBase64(sender.image)
    return render_template("senderEdit.html", title="Sender bearbeiten", header="Radio Sender bearbeiten", name=sender.name, url=sender.url, image=sender.image, imageData=imageData, canDelete=True)

@app.route("/radio/sender/add")
def doAddSender():
    return render_template("senderEdit.html", title="Neuer Sender", header="Neuer Sender", name= "", url="", image="", imageData="",canDelete=False)

@app.route("/radio/sender/delete")
def doDeleteSender():
    return redirect("/radio/sender")

@app.route("/radio/sender/save")
def doSaveSender():
    return redirect("/radio/sender")

@app.route("/radio/waketime/")
def doWaketime():
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/grid")
def doWaketimeGrid():
    acceptLanguages=str(request.accept_languages)
    mainLanguage = getMainLanguage(acceptLanguages)
    logging.debug(f"waketimeGrid(accept_languages:{acceptLanguages})")
    logging.debug(f">> mainLanguage = {mainLanguage}")
    return waketime.build_grid(mainLanguage)

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
    
    
