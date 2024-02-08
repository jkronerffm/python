import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj

Data = None
Filepath = "/var/radio/conf/radio.json"

def createSender(senderId, name, url, image):
    senderDict = {
        'id': senderId,
        'name': name,
        'url': url,
        'image': image
    }
    data = getData()
    data.sender.append(dictToObj.obj(senderDict))

def deleteSender(senderId):
    data = getData()
    index = [x.id for x in data.sender].index(senderId)
    del data.sender[index]
    writeData()
    
def getData():
    global Data
    global Filepath
    if Data == None:
        Data = dictToObj.objFromJson(Filepath)

    return Data

def getSender(senderId):
    data = getData()
    sender = [x for x in data.sender if x.id == senderId]
    return None if len(sender) == 0 else sender[0]

def writeData():
    global Filepath
    data = getData()
    jsonStr = dictToObj.objToJson(data)
    with open(Filepath, "w") as f:
        f.write(jsonStr)
        f.close()
    
def saveSender(senderId, name, url, image):
    sender = getSender(senderId)
    if sender != None:
        sender.name = name
        sender.url = url
        sender.image = image
    else:
        createSender(senderId, name, url, image)

    writeData()
    
