import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from flask import Flask, redirect, request, render_template, flash
import waketime
import radio
import status
from sound import Sound
import logging
from common import dictToObj
import base64
from urllib.request import url2pathname
from urllib.parse import urlparse
import uuid

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@app.route("/")   
@app.route("/radio")
def init():
    st = status.Status()
    statusData = st.get()
    return render_template("index.html", title="Radio Einstellungen", header="Radio Einstellungen", status = statusData)

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

def makePathnameFromUrl(url):
    p = urlparse(url)
    filepath = url2pathname(p.path)
    return filepath

def loadImageToBase64(url):
    if url == '':
        return None
    filepath = makePathnameFromUrl(url)
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
def doListRadioSender():
    o = dictToObj.objFromJson("/var/radio/conf/radio.json")
    senderList = o.sender
    imageList = []
    for sender in senderList:
        image = loadImageToBase64(sender.image)
        imageList.append(image)
    return render_template("radio.html", title="Radio Sender", header="Radio Sender", headerlist=["Name", "Adresse", "Bild"],senderList = senderList, imageList = imageList)

@app.route("/radio/sender/edit")
def doEditSender():
    senderId = request.args.get("id")
    logging.debug(f"doEditSender(id={senderId})")
    o = dictToObj.objFromJson("/var/radio/conf/radio.json")
    sender = [x for x in o.sender if x.id == senderId]
    if len(sender) > 0:
        sender = sender[0]
    else:
        return redirect("/radio/sender")
    logging.debug(f"doSenderEdit(id={senderId},sender={sender})")
    imageData=loadImageToBase64(sender.image)
    return render_template("senderEdit.html", title="Sender bearbeiten", header="Radio Sender bearbeiten", senderId = sender.id, name=sender.name, url=sender.url, image=makePathnameFromUrl(sender.image), imageData=imageData, canDelete=True, isNew=False)

@app.route("/radio/sender/add")
def doAddSender():
    senderId=str(uuid.uuid4())
    return render_template("senderEdit.html", title="Neuer Sender", header="Neuer Sender", senderId=senderId, canDelete=False, isNew=True)

@app.route("/radio/sender/delete")
def doDeleteSender():
    senderId = request.args.get('id')
    radio.deleteSender(senderId)
    return redirect("/radio/sender")

@app.route("/radio/sender/save")
def doSaveSender():
    for key in request.args.keys():
        logging.debug(f"doSaveSender(key={key}, value={request.args.get(key)})")
    senderId = request.args.get('id')
    name = request.args.get('name')
    url = request.args.get('url')
    image = request.args.get('imageFile')
    logging.debug("doSaveSender: try to access request.files")
    radio.saveSender(senderId, name, url, image)
    flash("Der Sender wurde erfolgreich gespeichert")
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
    jobList = waketime.createJobList(mainLanguage)
    headerList = waketime.getHeaderList(mainLanguage)
    logging.debug(f">> len(headerList) = {len(headerList)}, headerList={headerList}")    
    return render_template("waketimeGrid.html", header="Weckzeiten", headerList = headerList, jobList = jobList)

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
    senderList, editJob = waketime.createEdit(name)
    return render_template('waketimeEdit.html', header="Weckzeit bearbeiten", senderList=senderList, job=editJob, canDelete=True, canClone=True)

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
    timeAnnouncement = bool(request.args.get('timeannouncement', 'False')) if 'timeannouncement' in request.args else False
    waketime.save(name, theType, date, time, daysOfWeek, duration, sender, timeAnnouncement)
    flash("Die Weckzeit wurde erfolgreich gespeichert")
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/delete")
def doDeleteWaketime():
    logging.debug(f"doDeleteWaketime({request.args})")
    name=request.args.get('name', '')
    if name != '':
        waketime.delete(name)
    flash("Die Weckzeit wurde erfolgreich gelöscht")
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/add")
def doAddWaketime():
    logging.debug("doAddWaketime")
    senderList, editJob = waketime.add()
    return render_template('waketimeEdit.html', header="Weckzeit bearbeiten", senderList=senderList, job=editJob, canDelete=False, canClone=False)

@app.route("/radio/waketime/clone")
def doCloneWaketime():
    logging.debug("doCloneWaketime")
    name = request.args.get('name', None)
    if name == None:
        flash("Die Weckzeit kann nicht dupliziert werden")
        return redirect("/radio/waketime/grid")
    senderList, editJob = waketime.clone(name)
    logging.debug(f"doCloneWaketime(editJob={editJob})")
    flash("Die Weckzeit wurde erfolgreich dupliziert")
    return render_template('waketimeEdit.html', header="Weckzeit duplizieren", senderList=senderList, job=editJob, canDelete=False, canClone=False)

@app.route("/radio/sound/edit")
def doSoundEdit():
    sound = Sound()
    equalizers = sound.getEqualizers()
    selectedEqualizer = sound.getSelectedEqualizer()
    logging.debug(f"doSoundEdit(equalizers={equalizers}, selected={selectedEqualizer})")
    return render_template('sound.html', header="Sound Einstellungen", equalizers = equalizers, selectedEqualizer=selectedEqualizer)
    
@app.route("/radio/sound/change")
def doChangeSound():
    soundIndex = request.args.get('equalizer', None)
    if soundIndex != None:
        sound = Sound()
        sound.change(int(soundIndex))
    return redirect('/radio/sound/edit')
        
if __name__ == "main":
    logging.basicConfig(level="DEBUG")
    
    
