import sys
import os
from pathlib import Path
basepath = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()
sys.path.append(os.path.join(basepath, "have_internet"))
sys.path.append(os.path.join(basepath, "common"))
sys.path.append(os.path.join(basepath, "ircontrol"))
sys.path.append(os.path.join(basepath, "ipc"))
sys.path.append(os.path.join(basepath, "weather"))
from LogFormatter import LogFormatter
from xrandr import XRandr
from SimpleScheduler import SimpleScheduler
from os.path import isfile
import schedule
import json
import pygame
import pigpio
import dictToObj
import hexcolors
from ipc import StatusServer
from ircontrol import ircontrol, ButtonState
from ircontrol import LastPressed
from WeatherCalculator import WeatherCalculator as Weatherman
from area import Area
from pygame.event import Event
import math
from datetime import datetime, timedelta
from time import strftime, localtime
from ctypes import cast, POINTER
from RadioPlayer import *
import logging
from logging import handlers
from logging.handlers import RotatingFileHandler
from Scheduler import RadioScheduler
from have_internet import haveInternet
from urllib.parse import unquote, urlparse
from MetaBackgroundWorker import MetaBackgroundWorker
from filewatcher import WatchDog
from enum import Enum
import say
from Options import Options, ArgumentError
from common.Daemon import Daemon
import cProfile, pstats, io
import asyncio
from Xlib.ext import randr
import Monitor
from time import mktime

pygame.init()

MetaEvent = pygame.event.custom_type() + 1
SettingsEvent = pygame.event.custom_type() + 2
IrEvent = pygame.event.custom_type() + 3
SettingsFilepath = "/var/radio/conf/radio_settings.json"

class SettingsType(Enum):
    Waketime = 1
    Radio = 2
    Sound = 3

class IrState(Enum):
    ButtonDown = 1
    ButtonPressed = 2

class IrKey:
    Unused = 0
    Power = 1
    Pause = 2
    VolumeUp = 3
    VolumeDown = 4
    Left = 5
    Right = 6
    Up = 7
    Down = 8
    Display = 9
    Weather = 10
    Time = 11
    
    @staticmethod
    def FromButtonKey(buttonKey):
        KeyMapping = {
            'power': IrKey.Power,
            'ok': IrKey.Time,
            'vol+': IrKey.VolumeUp,
            'vol-': IrKey.VolumeDown,
            'up': IrKey.Up,
            'down': IrKey.Down,
            'left': IrKey.Left,
            'right': IrKey.Right,
            'display': IrKey.Display,
            'pause': IrKey.Pause,
            'weather': IrKey.Weather
        }
        result = 0
        if buttonKey in KeyMapping:
            result = KeyMapping[buttonKey]
        return result
    
class Colors:
    WHITE=(255,255,255)
    BLACK = (0,0,0)
    RED = (255, 0, 0)
    DARKRED = (128, 0, 0)
      
class Fonts:
    font14 = pygame.font.SysFont('Arial', 14, True, False)
    font18 = pygame.font.SysFont('Arial', 18, True, False)
    bigfont = pygame.font.SysFont('Arial', 128, True, False)
    medfont = pygame.font.SysFont('Arial', 64, True, False)
    
def point_in_rect(point,rect):
    x1, y1, w, h = rect
    x2, y2 = x1+w, y1+h
    x, y = point
    return (x > x1 and x < x2) and (y > y1 and y < y2)

def check_clickOnSender(pos):
    global data
    global focusOnSender
    global currentsender
    global radioPlayer
    
    focusOnSender = False
    for sender in radioPlayer.sender():
        if point_in_rect(pos, sender['rect']):
            if not haveInternet():
                sender = radioPlayer.getSenderByName(RadioPlayer.LocalList)
            currentsender = sender
            focusOnSender = True
            radioPlayer.play(currentsender['name'])
    return focusOnSender

def set_Volume(value):
    global radioPlayer
    radioPlayer.setVolume(value)

def get_VolumeValue(pos):
    global screenWidth
    global volDistX
    x = pos[0] - (screenWidth - volDistX)
    value = round(x*100/190)
    set_Volume(value)
    return value

def check_clickOnVolumeSettings(pos):
    global focusOnVolumeSettings
    global volume
    global screenWidth
    global screenHeight
    global volDistX
    global volDistY
    x0 = screenWidth - volDistX
    w = 190
    h = 60
    y0 = screenHeight - volDistY - h
    focusOnVolumeSettings = False
    focusOnVolumeSettings =  point_in_rect(pos, [x0, y0, w, h])
    if (focusOnVolumeSettings):
        x = pos[0] - x0
        v = math.floor(x/20)
        ymax = y0 - (10 + v*5)
        left,top, width, height = [x0, y0, w, h]
        right = x0 + w
        bottom = y0 + h
        posX, posY = pos
        focusOnVolumeSettings = posY < bottom and posY > ymax
        if focusOnVolumeSettings:
            volume = get_VolumeValue(pos)

    return focusOnVolumeSettings

def save_Settings(senderName, volume):
    settings = {
        "sender": senderName,
        "volume":volume
    }
    with open(SettingsFilepath, 'w') as outfile:
        json.dump(settings, outfile)

def load_Settings():
    global currentsender
    global currentname
    global volume
    global SettingsFilepath
    logging.debug("load_Settings")
    myFile = Path(SettingsFilepath)
    if not  myFile.exists():
        return

    with open(SettingsFilepath, 'r') as infile:
        global radioSender
        settings = json.load(infile)
        volume = settings['volume']
        currentname = settings['sender']
        for sender in radioPlayer.sender():
            if sender['name'] == currentname:
                currentsender = sender

def check_click(pos):
    global closeButton
    global active
    global focusOnSender
    global focusOnVolumeSettings
    global data
    global currentsender
    global radioPlayer
    
    logging.debug("check_click(%s)" % str(pos))
    if not active:
        return activate()
    if point_in_rect(pos, closeButton):
        deactivate()
    elif check_clickOnSender(pos):
        return True
    elif check_clickOnVolumeSettings(pos):
        return True

    return True

def switchBrightness():
    global monitor
    
    monitor.toggleBrightness()

def switchScreen():
    global monitor

    monitor.toggle()
    
def deactivate():
    global radioPlayer
    global currentsender
    global volume
    global active
    
    save_Settings(currentsender['name'], volume)
    active = False
    switchBrightness()
    radioPlayer.stop()
    
def activate():
    global active
    global radioPlayer
    global currentsender
    global brightness
    
    if active:
        deactivate()
        return True

    switchBrightness()
    active=True
    if currentsender != None:
        logging.debug(f"activate(currentsender={currentsender})")
        radioPlayer.play(currentsender['name'])
    return False

def draw_textRect(size, text, bg, fg, borderColor, font, alpha, padding=[0,0], center=False):
    s = pygame.Surface(size, pygame.SRCALPHA)
    s.set_alpha(0)
    pygame.draw.rect(s, borderColor, (0,0,size[0], size[1]))
    s.set_alpha(alpha)
    pygame.draw.rect(s, bg, (2, 2, size[0]-4,size[1]-4))
    #s.fill(bg)
    textfont = font.render(text, True, fg)
    if not center:
        x=padding[0]
        y=padding[1]
    else:
        x = (size[0] - textfont.get_width()) / 2
        y = (size[1] - textfont.get_height()) / 2
    s.blit(textfont, (x, y))
    return s

def draw_polygon_alpha(surface, color,  points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x, max_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)

def draw_speaker(surface, pos, factor, color):
    basePoints = [(0,1),(1,1),(2,0),(2, 4),(1,3),(0,3)]
    x0, y0 = pos
    points = [(x*factor+x0,y*factor+y0) for x, y in basePoints]
    draw_polygon_alpha(surface, color,points)

def draw_Volume_Range(surface, pos, dist, width, yDef, num, color):
    x, y = pos
    xDist, yDist = dist
    px0 = x;
    px1 = x+ volume / num * xDist - (xDist - width)
    py0 = y;
    py1 = y - volume / num * yDist - yDef

    for i in range(num):
        height = yDef + i * yDist
        pygame.draw.rect(surface, color, (x, y - height, width, height))
        x = x + xDist

    polygon = [(px0, py0), (px0, py0 - 10), (px1, py1), (px1, py0)]
    draw_polygon_alpha(surface, (255,255,255,128), polygon)

def drawCloseButton():
    global closeButtonPos
    global closeButton

    closeButton = pygame.draw.circle(screen, Colors.RED, closeButtonPos, 25)
    pygame.draw.circle(screen, Colors.WHITE, closeButtonPos, 20)
    pygame.draw.circle(screen, Colors.RED, closeButtonPos, 15)
    
def draw_sender(sender, x, y):
    global screenWidth, screenHeight
    global screenBorder
    global senderWidth, senderHeight
    global defImageWidth
    global screen
    global focusOnSender

    sender['rect'] = pygame.Rect(x,y,senderWidth, 60)
    imageDrawn = False
    imageWidth = senderWidth
    imageHeight = 60
    if sender['imagefile'] != '':
        imageurl = sender['imagefile']
        imagepath = unquote(urlparse(imageurl).path)
        image = sender['image'] if 'image' in sender else None
        if isfile(imagepath):
            if image == None:
                image = pygame.image.load(imagepath)
                sender['image'] = image
            (width, height) = image.get_size()
            imageWidth = defImageWidth
            imageHeight = imageWidth * height / width
            senderHeight = imageHeight if imageHeight > senderHeight else senderHeight
            sender['rect'].height = senderHeight
            scaledImage = pygame.transform.scale(image, (imageWidth, imageHeight))
            x_img = sender['rect'].left + (senderWidth - imageWidth) / 2
            y_img = sender['rect'].top if (senderHeight < imageHeight) else sender['rect'].top + (senderHeight - imageHeight) / 2
            screen.blit(scaledImage, (x_img, y_img))
            imageDrawn = True
    if not imageDrawn:
        s = draw_textRect(sender['rect'].size,sender['name'],Colors.WHITE, Colors.BLACK, Colors.BLACK, Fonts.font14, 200 if (buttonDown and focusOnSender and sender == currentsender) else 128, [10,10], True)
        screen.blit(s, sender['rect'].topleft)
    
    x = x + senderWidth
    if (x + senderWidth) > (screenWidth - screenBorder):
        x = screenBorder
        y = y + senderHeight + 10
        senderHeight = 60
    return (x, y, imageWidth, imageHeight)
    
def drawTitle(topY):
    global ScreenWidth, screenHeight
    with MetaBackgroundWorker.Lock:
        senderRect = draw_textRect((250,60), MetaBackgroundWorker.CurrentSender, Colors.WHITE, Colors.BLACK, Colors.WHITE, Fonts.font18,200,(10,10), True)
        xSender = (screenWidth - 250) / 2
        ySender = (screenHeight - topY - 240) / 2 + topY
        screen.blit(senderRect, [xSender, ySender])
        if MetaBackgroundWorker.CurrentTitle != None and MetaBackgroundWorker.CurrentTitle != "" and MetaBackgroundWorker != " - ":        
            (textWidth, textHeight) = Fonts.font18.size(MetaBackgroundWorker.CurrentTitle)
            textWidth += 50
            textHeight += 50
            titleRect = draw_textRect((textWidth, textHeight), MetaBackgroundWorker.CurrentTitle, Colors.WHITE, Colors.BLACK, Colors.WHITE, Fonts.font18, 200, (10, 10), True)
            xTitle = (screenWidth - textWidth) / 2
            yTitle = ySender + 80
            screen.blit(titleRect, [xTitle, yTitle])    
            
def draw_radio():
    global x, y
    global screen
    global screenWidth, screenHeight
    global screenBorder
    global data
    global senderWidth
    global senderHeight
    global currentname
    global closeButton
    global image, imagePos
    global buttonDown
    global focusOnSender
    global volume
    global radioPlayer
    global volDistX
    global volDistY
    global spkDistX
    global spkDistY
    
    pygame.draw.rect(screen,Colors.WHITE, (2,2,screenWidth - 4, screenHeight - 4))
    x = screenBorder
    y = screenBorder
    topY = 0
    screen.blit(image, imagePos)
    for sender in radioPlayer.sender():
        (x, y, imageWidth, imageHeight) = draw_sender(sender, x, y)
        if (y + imageHeight) > topY:
            topY = y + imageHeight
    currentname = Fonts.font18.render(currentsender['name'], True, Colors.BLACK)

    drawTitle(topY)
    drawCloseButton()
    # volume settings
    # f(x) = 10 + x * 5
    x = screenWidth - volDistX
    y = screenHeight - volDistY

    polygon = draw_Volume_Range(screen,(x,y), (20,5), 10, 10, 10, Colors.RED)

    volumestr = "{0}".format(volume)
    textRectVolume = draw_textRect((60, 30),volumestr, Colors.WHITE, Colors.BLACK, Colors.WHITE, Fonts.font18, 128,[5,5])
    screen.blit(textRectVolume, (x+200-10, y - 30))
    draw_speaker(screen, (screenWidth - spkDistX, screenHeight - spkDistY), 10, (160, 0, 0,200))

def todayAt(hour, minute=0, second=0, microsecond=0, now = None):
    if now == None:
        now = datetime.now()
    return now.replace(hour=hour, minute = minute, second = second, microsecond = microsecond)

def draw_clock():
    global screen
    global screenWidth, screenHeight
    global radioScheduler
    global timeColor
    
    nextRunTime = radioScheduler.nextRunTime()
    nextRunTimeDisplay = "Nächste Weckzeit: %s" % (nextRunTime.strftime('%d.%m.%Y %H:%M'))
    nrt = Fonts.font18.render(nextRunTimeDisplay, True, timeColor)
    screen.blit(nrt, [0, 0])
    now = datetime.fromtimestamp(mktime(localtime()))
    clock = now.strftime("%H:%M")
    cal = now.strftime("%d.%m.%Y")
    time = Fonts.bigfont.render(clock, True, timeColor)
    width = time.get_width()
    height = time.get_height()
    x = (screenWidth - width) / 2
    y = (screenHeight - height) / 2
    screen.blit(time, [x,y])
    calendar = Fonts.medfont.render(cal, True, timeColor)
    width = calendar.get_width()
    x = (screenWidth - width) / 2
    y = y + height + 20
    screen.blit(calendar, [x, y])

def jobHandler(job):
    global active
    logging.debug("radio.jobHandler")
    if job.name().startswith('start'):
        startHandler(job)
    elif job.name().startswith('stop') and active:
        stopHandler(job)
    elif job.name().startswith('cont'):
        contHandler(job)

def monitorOffAgain():
    logging.debug("monitorOffAgain()")
    monitorClient = Monitor.Client.GetInstance()
    enableScreenSaver(False)
    if monitorClient.isOn():
        logging.debug("monitorOffAgain(): switch monitor off")
        monitorClient.off()
        enableScreenSaver()
        
    schedule.clear('off_again')

def switchMonitor(on):
    monitorClient = Monitor.Client.GetInstance()
    monitorClient.switch(on)
    enableScreenSaver(not on)

def enableScreenSaver(enable = True):
## enable screensaver
    logging.debug(f"enableScreenSaver(enable={enable})")
    pygame.display.set_allow_screensaver(enable)
    
def toggleMonitor():
    global monitorScheduler
    global monitorOffByScheduler
    try:
        logging.debug(f"toggleMonitor(monitorScheduler={monitorScheduler})")
        monitorClient = Monitor.Client.GetInstance()
        logging.debug("toggleMonitor(): {monitorClient} was created")
        toggled = bool(monitorClient.toggle())
        enable = not toggled
        logging.debug(f"toggleMonitor(toggled={type(toggled)}({toggled}), enable={enable}, monitorOffByScheduler={monitorOffByScheduler})")
        enableScreenSaver(enable)
        if toggled and (monitorOffByScheduler or monitorClient.isOffTime()):
            logging.debug("toggleMonitor(): add job")
            monitorScheduler.addJob((schedule.every(monitorClient.getDelayOffTime()).seconds.tag('off_again'), "off_again"))
            monitorScheduler.addActionCallback("off_again", monitorOffAgain)
    except Exception as e:
        logging.exception(e)
        
def monitorOnCallback():
    global monitorOffByScheduler
    logging.debug("monitorOnCallback()")
    monitorClient = Monitor.Client.GetInstance()
    enableScreenSaver()
    if not monitorClient.isOn():
        monitorClient.on()
        enableScreenSaver(False)
    monitorOffByScheduler = False

def monitorOffCallback():
    global monitorOffByScheduler
    logging.debug("monitorOffCallback()")
    monitorClient = Monitor.Client.GetInstance()
    enableScreenSaver()
    if monitorClient.isOn():
        monitorClient.off()
    monitorOffByScheduler = True
    
def initMonitorScheduler(monitorScheduler):
    logging.debug("initMonitorScheduler()")
    monitorClient = Monitor.Client.GetInstance()
    logging.debug(f"initMonitorScheduler(offTime={monitorClient.getOffTime()}, onTime={monitorClient.getOnTime()})")
    if monitorClient.getOffTime() == "" or monitorClient.getOnTime() == "":
        return
    
    if monitorClient.getOffTime() == "test" or monitorClient.getOnTime == "test":
        now = datetime.now()
        tdOff = timedelta(minutes=1)
        tdOn = timedelta(minutes=4)
        tdOn2 = timedelta(minutes=6)
        offTime = (now + tdOff).strftime("%H:%M")
        onTime = (now + tdOn).strftime("%H:%M")
        onTime2 = (now +tdOn2).strftime("%H:%M")
    else:
        offTime = monitorClient.getOffTime()
        onTime = monitorClient.getOnTime()
        onTime2 = monitorClient.getOnTime2()
    offJob = monitorScheduler.addJob((schedule.every().day.at(offTime), "off"))
    onJobs = monitorScheduler.addJobs(([schedule.every().monday.at(onTime),
                                       schedule.every().tuesday.at(onTime),
                                       schedule.every().wednesday.at(onTime),
                                       schedule.every().thursday.at(onTime),
                                       schedule.every().friday.at(onTime),
                                       schedule.every().saturday.at(onTime2),
                                       schedule.every().sunday.at(onTime2)
                                       ], "on"))
    
    logging.debug(f"initMonitorScheduler(offJob={offJob}, onJob={onJobs})")
    monitorScheduler.addActionCallback("off", monitorOffCallback)
    monitorScheduler.addActionCallback("on", monitorOnCallback)
    
def startHandler(job):
    global radioPlayer
    global currentsender
    global active
    
    sendername = getSendernameFromJob(job) if haveInternet() else RadioPlayer.LocalList
    activeJob = job.id()
    logging.debug(f"startHandler(job={str(job)}, activeJob={activeJob})")
    if haveInternet() and hasattr(job, 'timeannouncement') and job.timeannouncement():
        (filepath, url) = say.say_time_with_greeting('de')
        radioPlayer.playUrl(url,True)

    switchMonitor(True)
    
    currentsender = radioPlayer.getSenderByName(sendername)
    radioPlayer.play(sendername)
    switchBrightness()
    active = True

def stopHandler(job):
    global radioPlayer
    global active
    radioPlayer.stop()
    switchBrightness()
    active = False

def contHandler(job):
    global radioPlayer
    global active
    global currentSender
    sendername = getSendernameFromJob(job) if haveInternet() else RadioPlayer.LocalList
    currentsender = radioPlayer.getSenderByName(sendername)
    radioPlayer.play(sendername)
    switchBrightness()
    active=True
    
def pauseRadio():
    global radioPlayer
    global radioScheduler
    global currentSender
    global active
    if not active:
        return

    contJob = radioScheduler.createContinueJob(currentsender["name"])
    if contJob == None:
        return
    logging.debug(f"pauseRadio(contJob={contJob})")
    switchBrightness()
    radioPlayer.stop()
    active = False
    

def getSendernameFromJob(job):
    global currentSender
    return job.sender() if job.sender() != None else currentsender["name"]

def onAddJob(name, job):
    global radioScheduler
    logging.debug("onAddJob(name=%s, job=%s)" % (name, str(job)))

def metaCallback(sender, title):
    global radioPlayer
    senderInUrl = radioPlayer.urlEndsWith(sender)
    if sender.endswith('.mp3'):
        MetaBackgroundWorker.CurrentTitle = sender[:len(sender)-4].replace('__', ' - ').replace('_', ' ')
        MetaBackgroundWorker.CurrentSender = "playlist"
    elif senderInUrl != None:
        MetaBackgroundWorker.CurrentTitle = title
        MetaBackgroundWorker.CurrentSender = senderInUrl["name"]
    else:
        MetaBackgroundWorker.CurrentSender = sender
        MetaBackgroundWorker.CurrentTitle  = title
    MetaBackgroundWorker.ChangeEvent.set()

def changeWaketime(filepath):
    global radioScheduler
    radioScheduler.shutdown()
    radioScheduler = RadioScheduler(filepath)
    radioScheduler.set_testing()
    radioScheduler.setJobHandler(jobHandler)
    radioScheduler.start()

def changeRadio(filepath):
    global radioPlayer
    radioPlayer.readConfigFile(filepath)

def changeSound(filepath):
    logging.debug(f"changeSound(filepath={filepath})")
    global radioPlayer
    global currentequalizer
    soundSettings = dictToObj.objFromJson(filepath)
    if hasattr(soundSettings, 'equalizer') and hasattr(soundSettings.equalizer, 'index'):
        radioPlayer.setEqualizerByIndex(soundSettings.equalizer.index)
    elif hasAttr(soundSettings, 'equalizer') and hasattr(soundSettings.equalizer, 'name'):
        radioPlayer.setEqualizerByName(soundSettings.equalizer.name)
    currentequalizer = soundSettings.equalizer

def waketimeHandler(filepath, modificationTime):
    logging.debug(f"waketimeHandler(filepath={filepath}): reload config file")
    event = pygame.event.Event(SettingsEvent, {'SettingsType': SettingsType.Waketime, 'Filepath': filepath})
    logging.debug(f">> post event {event}")
    pygame.event.post(event)

def radioHandler(filepath, modificationTime):
    logging.debug(f"radioHandler(filepath={filepath}): load config file")
    event = pygame.event.Event(SettingsEvent, {'SettingsType': SettingsType.Radio, 'Filepath': filepath})
    logging.debug(f">> post event {event}")
    pygame.event.post(event)

def soundHandler(filepath, modificationTime):
    logging.debug(f"soundHandler(filepath={filepath}): load config file")
    event = pygame.event.Event(SettingsEvent, {'SettingsType': SettingsType.Sound, 'Filepath': filepath})
    logger.debug(f">> post event {event}")
    pygame.event.post(event)

def monitorHandler(filepath, modificationTime):
    logging.debug(f"monitorHandler(filepath={filepath}): release monitorClient")
    Monitor.Client.ReleaseInstance()
    
def buttonDown(buttonCode):
    buttonKey = ircontrol.GetHashKey(buttonCode)
    eventKey = IrKey.FromButtonKey(buttonKey)
    event = pygame.event.Event(IrEvent, {'IrState': IrState.ButtonDown, 'IrKey': eventKey})
    logging.debug(f"buttonDown(event={event})")
    pygame.event.post(event)
    
def buttonPressed(buttonCode):
    buttonKey = ircontrol.GetHashKey(buttonCode)
    eventKey = IrKey.FromButtonKey(buttonKey)
    event = pygame.event.Event(IrEvent, {'IrState': IrState.ButtonPressed, 'IrKey': eventKey})
    logging.debug(f"buttonPressed(event={event})")
    pygame.event.post(event)
    
def irCallback(buttonCode, buttonState):
    if buttonState != None:
        buttonState.setButtonDown(buttonCode)
        
def toggleVolume(up):
    global volume
    if up:
        if volume < 100:
            volume+=2
    else:
        if volume > 0:
            volume -= 2
    set_Volume(volume)

def sayMessage(message:say.Message.Key):
    global active
    global radioPlayer
    
    message = say.Message[message]
    radioPlayer.playUrl(message, True)
    if active:
        radioPlayer.play(currentsender["name"])
    
def sayTime():
    global active
    global currentsender
    if active:
        radioPlayer.stop()

    if haveInternet():
        (filepath, url) = say.say_time('de', fuzzy=False)
        radioPlayer.playUrl(url, True)
        logging.debug(f"sayTime(url={url})")
        os.remove(filepath)
    else:
        sayMessage(say.Message.Key.NoInternet)
        
    if active:
        radioPlayer.play(currentsender['name'])

def weatherCallback(weather):
    text = Weatherman.HumanUnderstandableForecast(weather)
    logging.debug(f"weatherCallback(text={text})")
    filepath, url = say.say(text, "de")
    radioPlayer.playUrl(url, True)
    os.remove(filepath)

def sayWeather():
    global active
    global currentsender

    if active:
        radioPlayer.stop()
        
    if haveInternet():
        try:
            area = Area("Frankfurt am Main", "Germany", "Europe/Berlin", 50.11, 8.68)
            logging.debug(f"sayWeather(area={area})")
            weatherman = Weatherman(area, None)
            freeSpeechForecast = Weatherman.HumanUnderstandableForecast(weatherman.run())
            asyncio.run(say.say_multipleLineOutput(freeSpeechForecast, "de", radioPlayer))
        except Exception as e:
            logging.exception(f"an error has been raised: {e}. Please contact the developer!")
    if active:
        radioPlayer.play(currentsender['name'])
        
def nextSender():
    global radioPlayer
    global currentsender
    nextSender = radioPlayer.getNextSender(currentsender["name"])
    radioPlayer.play(nextSender['name'])
    currentsender = nextSender

def previousSender():
    global radioPlayer
    global currentsender
    previousSender = radioPlayer.getPreviousSender(currentsender["name"])
    radioPlayer.play(previousSender['name'])
    currentsender = previousSender

def nextEqualizer():
    global radioPlayer
    radioPlayer.nextEqualizer()

def previousEqualizer():
    global radioPlayer
    radioPlayer.previousEqualizer()

def statusCallback():
    global active
    global currentsender
    global currentequalizer
    global volume
    global radioScheduler
    logging.debug("statusCallback()")
    nextRunTime = radioScheduler.nextRunTime()
    nextRunTimeDisplay = nextRunTime.strftime('%d.%m.%Y %H:%M')
    return {"running": True, "active": active, "current_sender": currentsender['name'], "volume": volume, "equalizer": currentequalizer.name, "next_runtime": nextRunTimeDisplay}

def loadBackgroundImage(backgroundfile):
    global image
    global imagePos
    global screenWidth
    global screenHeight
    
    image = pygame.image.load(backgroundfile)
    image = pygame.transform.scale(image, [screenWidth, screenHeight])
    imagePos = ((screenWidth - image.get_width())/2,(screenHeight - image.get_height()) if (screenHeight >  image.get_height()) else 0)

def initProfiler():
    profiler = cProfile.Profile()
    profiler.enable()
    return profiler

def saveStats(profiler, filename):
    if profiler != None:
        profiler.disable()
        logDir = "/var/radio/log"
        logFile = filename
        if not os.path.exists(logDir):
            os.mkdir(logDir, mode=777)
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats(options.statKey())
        stats.print_stats()
        with open(os.path.join(logDir, logFile), "w") as f:
            f.write(s.getvalue())
    
if __name__ == "__main__":
## initialization
## get commandline params
    try:
        options = Options.Get(sys.argv[0], sys.argv[1:])
    except ArgumentError:
        printUsage(sys.argv[0])
        sys.exit(-1)

    profiler = initProfiler() if options.profiling() else None

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if options.debug() else logging.FATAL)
    logFormatter = LogFormatter()    
    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    console_handler.setFormatter(logFormatter)
    logDir = "/var/radio/log"
    logFilename = "radio.log"
    logFilepath = os.path.join(logDir, logFilename)
    file_handler = RotatingFileHandler(logFilepath, maxBytes=4096, backupCount=5)
    file_handler.setFormatter(logFormatter)
    logger.addHandler(file_handler)
    logger.debug(f"start radio")
## initialize ircontrol
    ircontrol.ReadHashes("/var/radio/remotecontrol/sony_RM-SED1.json")
    daemon = Daemon("pigpio")
    daemon.start()
    
    pi = pigpio.pi()
    buttonState = ButtonState.Start(buttonDown, buttonPressed)
    irc = ircontrol(pi, 17, irCallback, buttonState = buttonState, timeout=5)
## initialize display sizes    
    if options.fullscreen():
        info = pygame.display.Info()
        screenWidth = info.current_w
        screenHeight = info.current_h
    elif options.size() != None:
        screenWidth = int(options.size()[0])
        screenHeight = int(options.size()[0])
    else:
        screenWidth = 1024
        screenHeight = screenWidth * 9 / 16
    volDistX = 300
    volDistY = 10
    spkDistX = 350
    spkDistY = 50
    activeJob = None
    screenBorder = 10
    senderWidth = (screenWidth - 2 * screenBorder) / 6
    senderHeight = 60
    defImageWidth = 96
    volume = 0
    screen = pygame.display.set_mode((screenWidth,screenHeight), pygame.NOFRAME)
    focusOnVolumeSettings = False
    
## initialize pathnames
    rootDir = "/var/radio"
    confDir = "conf"
    confFilepathRadio = os.path.join(rootDir, confDir, "radio.json")
    confFilepathWaketime = os.path.join(rootDir, confDir, "waketime.json")
    confFilepathSound = os.path.join(rootDir, confDir, "sound.json")
    confFilepathMonitor = os.path.join(rootDir, confDir, "monitor.json")
    
    radioPlayer = RadioPlayer(confFilepathRadio)
    load_Settings()
    hexCol = radioPlayer.timeColor()
    timeColor = hexcolors.hexToRgb(hexCol) if hexCol != None else Colors.DARKRED
    monitor = Monitor.Monitor(delay=5.0)
## initialize radioScheduler    
    radioScheduler = RadioScheduler(confFilepathWaketime)
    radioScheduler.setAddJobHandler(onAddJob)
    radioScheduler.setJobHandler(jobHandler)
    radioScheduler.set_testing()
    radioScheduler.start()
## initialize watchDog    
    watchDog = WatchDog.GetInstance()
    watchDog.watch(confFilepathRadio, radioHandler)
    watchDog.watch(confFilepathWaketime, waketimeHandler)
    watchDog.watch(confFilepathSound, soundHandler)
    watchDog.watch(confFilepathMonitor, monitorHandler)
    running = True
    active = False
    clock = pygame.time.Clock()
## initialize display    
    backgroundfile = radioPlayer.background()
    iconFile = radioPlayer.icon()
    defImageWidth = radioPlayer.imageWidth()
    icon = pygame.image.load(iconFile)
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Radio")
    loadBackgroundImage(backgroundfile)
    
    closeButtonPos = (screenWidth - screenBorder - 25,screenHeight - screenBorder - 25)
    buttonDown=False
    changeSound("/var/radio/conf/sound.json")
    MetaBackgroundWorker.Create(radioPlayer, metaCallback)
    StatusServer.StartThread("radio", statusCallback)
    logging.debug("currentsender=%s" % currentsender)
    if options.profiling():
        saveStats(profiler, "initStats.log")
        profiler = initProfiler()
    monitor.setDimValue(radioPlayer.brightness())
    monitor.dim()
## start SimpleScheduler for Monitor
    monitorOffByScheduler = False
    monitorScheduler = SimpleScheduler()
##    initMonitorScheduler(monitorScheduler)
    monitorScheduler.start()
## start main loop
    logging.debug("start main loop")
    while running:
        try:
            screen.fill(Colors.BLACK)
            if active:
                draw_radio()
            else:
                draw_clock()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.debug("quit pygame")
                    running=False
                    break;
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    if not check_click(event.pos):
                        active=True
                    else:
                        buttonDown=True
                    break;
                elif event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION:
                    if focusOnVolumeSettings and buttonDown and check_clickOnVolumeSettings(event.pos):
                        volume = get_VolumeValue(event.pos)
                    break;
                elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                    buttonDown = False
                elif event.type == SettingsEvent:
                    if event.SettingsType == SettingsType.Waketime:
                        changeWaketime(event.Filepath)
                    elif event.SettingsType == SettingsType.Radio:
                        changeRadio(event.Filepath)
                        loadBackgroundImage(radioPlayer.background())
                        timeColor = hexcolors.hexToRgb(radioPlayer.timeColor())
                        newBrightness = radioPlayer.brightness()
                        defImageWidth = radioPlayer.imageWidth()
                        logging.debug(f"main loop: new defImageWidth={defImageWidth}")
                        monitor.setDimValue(newBrightness)
                    elif event.SettingsType == SettingsType.Sound:
                        changeSound(event.Filepath)
                elif event.type == IrEvent:
                    if event.IrState == IrState.ButtonPressed:
                        if event.IrKey == IrKey.Power:
                            activate()
                        if event.IrKey == IrKey.Pause and active:
                            logging.debug(f"IRControl-->Pause: make a pause")
                            pauseRadio()
                        elif event.IrKey == IrKey.Down:
                            logging.debug(f"switch Equalizer to next preset")
                            nextEqualizer()
                        elif event.IrKey == IrKey.Up:
                            logging.debug(f"switch Equalizer to previous preset")
                            previousEqualizer()
                        elif event.IrKey == IrKey.Left and active:
                            logging.debug(f"IRControl-->Left: switch to previous radio sender")
                            previousSender()
                        elif event.IrKey == IrKey.Right and active:
                            logging.debug(f"IRControl-->Right: switch to next radio sender")
                            nextSender()
                        elif event.IrKey == IrKey.Display:
                            logging.debug(f"IRControl-->Display: switch screen on/off")
                            if not active:
                                toggleMonitor()
                        elif event.IrKey == IrKey.Time:
                            sayTime()
                        elif event.IrKey == IrKey.Weather:
                            sayWeather()
                    elif event.IrState == IrState.ButtonDown:
                        if event.IrKey == IrKey.VolumeUp and active:
                            logging.debug(f"IRControl-->VolumeUp: increase volume")
                            toggleVolume(True)
                        elif event.IrKey == IrKey.VolumeDown and active:
                            logging.debug(f"IRControl-->VolumeDown: decrease volume")
                            toggleVolume(False)
            pygame.display.flip()
            clock.tick(60)
        except KeyboardInterrupt:
            event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(event)
            continue
    logging.debug("exit the pygame app")
    switchMonitor(on = True)
    pygame.quit()
    radioPlayer.stop()
    radioScheduler.shutdown()
    pi.stop()
    daemon.kill()
    if options.profiling():
        saveStats(profiler, "loopStats.log")
    monitor.light()
    monitorScheduler.stop()
    sys.exit()
