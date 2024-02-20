import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from fuzzyTime import fuzzyTime
import gtts
import uuid
from datetime import datetime
import RadioPlayer
import logging
import pathlib
import time

def play(filepath):
    global radioPlayer
    radioPlayer.playUrl(filepath)
    
def say(text, language):
    logging.debug("(text=%s)" % (text))
    tts = gtts.gTTS(text, lang=language)
    filename = str(uuid.uuid4()) + ".mp3"
    filepath = os.path.join("/tmp", filename)
    tts.save(filepath)
    url = pathlib.Path(filepath).as_uri()
    return (filepath, url)

def get_greeting(time):
    if time.hour >= 3 and time.hour <= 11:
        return "Guten Morgen."
    if time.hour > 11 and time.hour < 18:
        return "Guten Tag."
    return "Gute Nacht."

def get_time():
    now = datetime.now()
    currentTime = fuzzyTime.get_fuzzy_time(now)
    text = f"Es ist {currentTime}."
    return (now, text)
    
def say_time(language):
    now, text = get_time()
    logging.debug(f"say_time(language={language}): {text}")
    return say(text, language)

def say_time_with_greeting(language):
    now, timeText = get_time()
    greeting = get_greeting(now)
    text = f"{greeting}. {timeText}"
    return say(text, language)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer.RadioPlayer("/var/radio/conf/radio.json")
    radioPlayer.setVolume(75)
    filepath, url = say_time_with_greeting('de')
    radioPlayer.playUrl(url, True)
    
