import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from flask import Flask, redirect, request, render_template, flash,jsonify
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
import pathlib
from LogFormatter import LogFormatter
from logging import handlers
from logging.handlers import RotatingFileHandler
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
    if os.path.exists(filepath):
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
    else:
        return None

@app.route("/radio/sender/")
def doListRadioSender():
    o = dictToObj.objFromJson("/var/radio/conf/radio.json")
    senderList = o.sender
    imageList = []
    for sender in senderList:
        image = loadImageToBase64(sender.imagefile)
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
    playlist = []
    if sender.url.startswith('file://'):
        p = urlparse(sender.url)
        filepath = url2pathname(p.path)
        if sender.url.endswith('.m3u'):
            # read m3u
            with open(filepath, 'r') as f:
                playlist = [filename.strip() for filename in f.readlines()]
        else:
            # read files from folder
            playlist = [filename for filename in os.listdir(filepath) if filename.endswith(('.mp3',))]
    imageData=loadImageToBase64(sender.imagefile)
    logging.debug(f"doEditSender(playlist={playlist}")
    shuffle = hasattr(sender, "shuffle") and sender.shuffle
    return render_template("senderEdit.html", title="Sender bearbeiten", header="Radio Sender bearbeiten", senderId = sender.id, name=sender.name, url=sender.url, shuffle=shuffle, image=makePathnameFromUrl(sender.imagefile), imageData=imageData, canDelete=True, isNew=False, playlist=playlist)

@app.route("/radio/sender/add")
def doAddSender():
    senderId=str(uuid.uuid4())
    return render_template("senderEdit.html", title="Neuer Sender", header="Neuer Sender", senderId=senderId, canDelete=False, isNew=True, playlist=[])

@app.route("/radio/sender/delete")
def doDeleteSender():
    senderId = request.args.get('id')
    radio.deleteSender(senderId)
    return redirect("/radio/sender")

basepath = "/var/radio/"
picspath = os.path.join(basepath, "pics")
musicpath = os.path.join(basepath, "music")

def saveUploadFile(file, dest):
    if file != None and file.filename != "":
        filepath = os.path.join(dest, file.filename)
        file.save(filepath)
        return filepath
    else:
        return None
    
def saveUploadList(fileList, dest):
    savedFiles=[]
    for file in fileList:
        filepath = saveUploadFile(file, dest)
        savedFiles.append(filepath)
    return savedFiles
    
@app.route("/radio/sender/save", methods=["GET", "POST"])
def doSaveSender():
    logging.debug(f"doSaveSavender()")
    if request.method == "POST":
        logging.debug(f">> post")
        for key in request.form.keys():
            logging.debug(f">>>>key={key}, value={request.form.get(key)}")
        senderId = request.form.get('id')
        name = request.form.get('name')
        url = request.form.get('url')
        if 'imageFile' in request.files:
            filepath = saveUploadFile(request.files['imageFile'], picspath)
        else:
            filepath = request.form.get('imagefilepath')
        radio.saveSender(senderId, name, url, filepath)
        flash("Der Sender wurde erfolgreich gespeichert")
        return redirect("/radio/sender")
    return '';
    
@app.route("/radio/waketime/")
def doWaketime():
    return redirect("/radio/waketime/grid")

@app.route("/radio/waketime/grid")
def doWaketimeGrid():
    acceptLanguages=str(request.accept_languages)
    mainLanguage = getMainLanguage(acceptLanguages)
    jobList = waketime.createJobList(mainLanguage)
    headerList = waketime.getHeaderList(mainLanguage)
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
    volume = request.args.get('volume', '')
    theType= request.args.get('dateOrCron', "cron")
    timeAnnouncement = bool(request.args.get('timeannouncement', 'False')) if 'timeannouncement' in request.args else False
    waketime.save(name, theType, date, time, daysOfWeek, duration, sender, volume, timeAnnouncement)
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
    
@app.route("/radio/misc")
def doMisc():
    imageList = [filename for filename in os.listdir('/var/radio/background') if filename.endswith(('.jpg', '.jpeg', '.png', '.svg'))]
    radioData = dictToObj.objFromJson(os.path.join(basedir, confdir, conffile))
    monitorData = dictToObj.objFromJson(os.path.join(basedir, confdir, monitorConfFile))
    selectedImage = os.path.basename(radioData.background)
    imageData = loadImageToBase64(pathlib.Path(radioData.background).as_uri())
    timeColor = radioData.timecolor if hasattr(radioData, "timecolor") else "#800000"
    brightness = radioData.brightness if hasattr(radioData, "brightness") else "20"
    imageWidth = radioData.imageWidth if hasattr(radioData, "imageWidth") else "64"
    offTime = monitorData.time.off
    onTime = monitorData.time.on
    delayOff = monitorData.time.delayOff
    return render_template('miscEdit.html', header='Sonstiges', imageList=imageList, selectedImage=selectedImage, imageData=imageData, timeColor=timeColor,brightness=brightness, imageWidth=imageWidth, offTime=offTime, onTime=onTime, delayOff = delayOff)
    
basedir = "/var/radio/"
confdir = "conf"
bgdir = "background"
conffile = "radio.json"
monitorConfFile = "monitor.json"

@app.route("/radio/misc/save")
def doSaveMisc():
    background = {}
    background["name"] = request.args.get("background", None)
    if background["name"] == None:
        flash("Kein Hintergrund ausgewählt!")
        return redirect("/radio/misc")
        
    background["filepath"] = os.path.join(basedir, bgdir, background["name"])
    if not os.path.exists(background["filepath"]):
        flash("Datei für Hintergrundbild existiert nicht")
        return redirect("/radio/misc")
        
    confFilepath = os.path.join(basedir, confdir, conffile)
    monitorConfFilepath = os.path.join(basedir, confdir, monitorConfFile)
    background["url"] = pathlib.Path(background["filepath"]).as_uri()
    logging.debug(f"doSavebackground(background={background})")
    radioData = dictToObj.objFromJson(confFilepath)
    monitorData = dictToObj.objFromJson(monitorConfFilepath)
    radioData.background= background["filepath"]
    timecolor = request.args.get("timecolor", "#800000")
    brightness = request.args.get("brightness", "20")
    imageWidth = request.args.get("imageWidth", "64")
    offTime = request.args.get("offTime", "22:00")
    onTime = request.args.get("onTime", "06:00")
    delayOff = request.args.get("delayOff", "15")
    radioData.timecolor = timecolor
    radioData.brightness = brightness
    radioData.imageWidth = imageWidth
    monitorData.time.off = offTime
    monitorData.time.on = onTime
    monitorData.time.delayOff = delayOff
    logging.debug(f"timecolor={timecolor}")
    dictToObj.objToJsonFile(radioData, confFilepath)
    dictToObj.objToJsonFile(monitorData, monitorConfFilepath)
    return redirect("/radio")
        
@app.route("/radio/background/get")
def getBackgroundImages():
    filename = request.args.get('image', None)
    if filename != None:
        logging.debug(f"getBackgroundImage(filename={filename})")
        imageData = loadImageToBase64(f"file:///var/radio/background/{filename}")
    return jsonify(b64Image = imageData);
    
@app.route("/radio/background/save", methods=["GET","POST"])
def saveBackgroundImage():
    logging.debug(f"getBackgroundImage(request={request})")
    if request.method == "POST":
        logging.debug(f" >> files={request.files}")
        if "file" in request.files:
            file = request.files['file']
            logging.debug(f" >> filename = {file.filename}")
            saveUploadFile(file, "/var/radio/background")
    backgroundImages = [filename for filename in os.listdir('/var/radio/background') if filename.endswith(('.jpg', '.jpeg', '.png', '.svg'))]
    return jsonify(background= backgroundImages)
  
if __name__ == "main":
    logger = logging.getLogger()
    
    logger.setLevel(level="DEBUG")
    logFormatter = LogFormatter()
#    console_handler = logging.StreamHandler(sys.stdout)
#    logger.addHandler(console_handler)
#    console_handler.setFormatter(logFormatter)
    logDir = "/var/radio/log"
    logFilename = "webapp.log"
    logFilepath = os.path.join(logDir, logFilename)
    file_handler = RotatingFileHandler(logFilepath, mode='w', maxBytes=4096, backupCount=5)
    file_handler.setFormatter(logFormatter)
    logger.addHandler(file_handler)
    
