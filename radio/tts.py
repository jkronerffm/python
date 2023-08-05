import pyttsx3
import gtts
import playsound
import uuid
import os
import datetime
from RadioPlayer import RadioPlayer
import pathlib
import logging

def speakWithpyttsx3(text, language):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    print(dir(voices[0]))
    german = -1
    index = 0
    for voice in voices:
        if german == -1 and voice.name  == language:
            german = index
        index += 1

    print(str(voices[german]))
    engine.setProperty("voice", voices[german])
    engine.say(text)
    engine.runAndWait()

def speakWithGtts(text, language, radioPlayer = None):
    tts = gtts.gTTS(text, lang=language)
    filename = str(uuid.uuid4()) + ".mp3"
    filepath = os.path.join("/tmp", filename)
    tts.save(filepath)
    print(filepath)
    if radioPlayer == None:
        playsound.playsound(filepath)
    else:
        url = pathlib.Path(filepath).as_uri()
        radioPlayer.playUrl(url)

def speakCurrentTime():
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    logging.debug("speakCurrentTime(time=%s)" % str(time))
    speakWithGtts("%s, es ist %s" % (getGreeting(now),time), "de")
    
def getGreeting(time):
    if time.hour < 11:
        return "Guten Morgen"
    elif time.hour >= 11 and time.hour < 18:
        return "Guten Tag"
    else:
        return "Guten Abend"

if __name__ == "__main__":
    radioPlayer = RadioPlayer("radio.json")
    radioPlayer.setVolume(10)
