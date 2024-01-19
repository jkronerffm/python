import sys
sys.path.append("/home/jkroner/Documents/python/have_internet")
from os.path import isfile
import json
import pygame
import math
from time import strftime, localtime
from pathlib import Path
from ctypes import cast, POINTER
from RadioPlayer import *
import logging
from Scheduler import RadioScheduler
from have_internet import haveInternet
from urllib.parse import unquote, urlparse

def point_in_rect(point,rect):
    x1, y1, w, h = rect
    x2, y2 = x1+w, y1+h
    x, y = point
    if (x1 < x and x < x2):
        if (y1 < y and y < y2):
            return True
    return False

def check_clickOnSender(pos):
    global data
    global focusOnSender
    global currentsender
    global radioPlayer
    
    focusOnSender = False
    for sender in radioPlayer.sender():
        if point_in_rect(pos, sender['rect']):
            if not haveInternet():
                sender = radioPlayer.getSenderByName('my music')
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
    with open('radio_settings.json', 'w') as outfile:
        json.dump(settings, outfile)

def load_Settings():
    global currentsender
    global currentname
    global volume

    logging.debug("load_Settings")
    myFile = Path('radio_settings.json')
    if not  myFile.exists():
        return

    with open('radio_settings.json', 'r') as infile:
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
        if currentsender != None:
            logging.debug("play(%s)" % currentsender)
            radioPlayer.play(currentsender['name'])
        return False;
    if point_in_rect(pos, closeButton):
        save_Settings(currentsender['name'], volume)
        active = False
        radioPlayer.stop()
    elif check_clickOnSender(pos):
        return True
    elif check_clickOnVolumeSettings(pos):
        return True

    return True

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

def draw_sender(sender, x, y):
    global screenWidth, screenHeight
    global screenBorder
    global senderWidth, senderHeight
    global screen
    global BLACK, WHITE, RED

    sender['rect'] = pygame.Rect(x,y,senderWidth, senderHeight)
    imageDrawn = False
    imageWidth = senderWidth
    imageHeight = 60
    if sender['image'] != '':
        imageurl = sender['image']
        imagepath = unquote(urlparse(imageurl).path)
        if isfile(imagepath):
            image = pygame.image.load(imagepath)
            (width, height) = image.get_size()
            imageWidth = senderWidth
            imageHeight = imageWidth * height / width
            scaledImage = pygame.transform.scale(image, (imageWidth, imageHeight))
            sender['rect'] = pygame.Rect(x, y, imageWidth, imageHeight)
            screen.blit(scaledImage, sender['rect'].topleft)
            imageDrawn = True
    if not imageDrawn:
        s = draw_textRect(sender['rect'].size,sender['name'],WHITE, BLACK, BLACK, font14, 200 if (buttonDown and focusOnSender and sender == currentsender) else 128, [10,10], True)
        screen.blit(s, sender['rect'].topleft)
    
    x = x + senderWidth
    if x > (screenWidth - screenBorder):
        x = screenBorder
        y = y + senderHeight
    return (x, y, imageWidth, imageHeight)
    
def draw_radio():
    global x, y
    global screen
    global screenWidth, screenHeight
    global screenBorder
    global data
    global senderWidth
    global senderHeight
    global font14, font18
    global currentname
    global closeButton
    global ccloseButtonPos
    global image, imagePos
    global BLACK, WHITE, RED
    global buttonDown
    global focusOnSender
    global volume
    global radioPlayer
    global volDistX
    global volDistY
    global spkDistX
    global spkDistY
    pygame.draw.rect(screen,WHITE, (2,2,screenWidth - 4, screenHeight - 4))
    x = screenBorder
    y = screenBorder
    topY = 0
    screen.blit(image, imagePos)
    for sender in radioPlayer.sender():
        (x, y, imageWidth, imageHeight) = draw_sender(sender, x, y)
        if (y + imageHeight) > topY:
            topY = y + imageHeight
    currentname = font18.render(currentsender['name'], True, BLACK)
    titleRect = draw_textRect((250,60), currentsender['name'], WHITE, BLACK, WHITE, font18,200,(10,10), True)
    screen.blit(titleRect, [350, topY + 20])
    closeButton = pygame.draw.circle(screen, RED, closeButtonPos, 25)
    pygame.draw.circle(screen, WHITE, closeButtonPos, 20)
    pygame.draw.circle(screen, RED, closeButtonPos, 15)
    # volume settings
    # f(x) = 10 + x * 5
    x = screenWidth - volDistX
    y = screenHeight - volDistY

    polygon = draw_Volume_Range(screen,(x,y), (20,5), 10, 10, 10, RED)

    volumestr = "{0}".format(volume)
    textRectVolume = draw_textRect((60, 30),volumestr, WHITE, BLACK, WHITE, font18, 128,[5,5])
    screen.blit(textRectVolume, (x+200-10, y - 30))
    draw_speaker(screen, (screenWidth - spkDistX, screenHeight - spkDistY), 10, (160, 0, 0,200))

def draw_clock():
    global screen
    global bigfont, medfont
    global screenWidth, screenHeight
    now = localtime()
    clock = strftime("%H:%M",now)
    cal = strftime("%d.%m.%Y", now)
    time = bigfont.render(clock, True, WHITE)
    width = time.get_width()
    height = time.get_height()
    x = (screenWidth - width) / 2
    y = (screenHeight - height) / 2
    screen.blit(time, [x,y])
    calendar = medfont.render(cal, True, WHITE)
    width = calendar.get_width()
    x = (screenWidth - width) / 2
    y = y + height + 20
    screen.blit(calendar, [x, y])

def jobHandler(job):
    global active
    if job.name().startswith('start'):
        startHandler(job)
    elif job.name().startswith('stop') and active:
        stopHandler(job)
        
def startHandler(job):
    global radioPlayer
    global currentsender
    global active
    logging.debug("startHandler" + str(job))
    sendername = job.sender() if job.sender() != None else currentsender['name']
    sender = radioPlayer.getSenderByName(sendername)
    if not haveInternet():
        sender = radioPlayer.getSenderByName('my music')
    currentsender = sender
    radioPlayer.play(sender['name'])
    active = True

def stopHandler(job):
    global radioPlayer
    global active
    radioPlayer.stop()
    active = False
    
def onAddJob(name, job):
    global radioScheduler
    print("onAddJob(name=%s, job=%s)" % (name, str(job)))
    
logging.basicConfig(level = logging.DEBUG)
pygame.init()
if len(sys.argv) >= 2:
    screenWidth = int(sys.argv[1])
    screenHeight = int(sys.argv[2])
else:
    screenWidth = 800
    screenHeight = 480
volDistX = 300
volDistY = 10
spkDistX = 350
spkDistY = 50

screenBorder = 10
volume = 0
screen = pygame.display.set_mode((screenWidth,screenHeight), pygame.NOFRAME)
focusOnVolumeSettings = False

radioPlayer = RadioPlayer("radio.json")
senderWidth = (screenWidth - 2 * screenBorder) / 6
senderHeight = 60
load_Settings()
radioScheduler = RadioScheduler('waketime.json')
radioScheduler.setAddJobHandler(onAddJob)
radioScheduler.setJobHandler(jobHandler)
radioScheduler.set_testing()
radioScheduler.start()
running = True
active = False
WHITE=(255,255,255)
BLACK = (0,0,0)
RED = (255, 0, 0)
clock = pygame.time.Clock()
backgroundfile = radioPlayer.background()
image = pygame.image.load(backgroundfile)
image = pygame.transform.scale(image, [screenWidth, screenHeight])
imagePos = ((screenWidth - image.get_width())/2,(screenHeight - image.get_height()) if (screenHeight >  image.get_height()) else 0)
font14 = pygame.font.SysFont('Arial', 14, True, False)
font18 = pygame.font.SysFont('Arial', 18, True, False)
bigfont = pygame.font.SysFont('Arial', 128, True, False)
medfont = pygame.font.SysFont('Arial', 64, True, False)
closeButtonPos = (screenWidth - screenBorder - 25,screenHeight - screenBorder - 25)
buttonDown=False
logging.debug("currentsender=%s" % currentsender)
while running:
    try:
        screen.fill(BLACK)
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
    
        pygame.display.flip()
        clock.tick(60)
    except KeyboardInterrupt:
        running = False
        continue
logging.debug("exit the pygame app")
pygame.quit()
radioPlayer.stop()
sys.exit()
