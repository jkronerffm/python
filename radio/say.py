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
import urllib
import time
import locale
from enum import Enum

def play(filepath):
    global radioPlayer
    radioPlayer.playUrl(filepath)
    
def say(text, language):
    logging.debug(f"say(text={text}, language={language})")
    tts = gtts.gTTS(text, lang=language)
    filename = str(uuid.uuid4()) + ".mp3"
    logging.debug(f"say(filename={filename})")
    filepath = os.path.join("/tmp", filename)
    logging.debug(f"say(filepath={filepath})")
    tts.save(filepath)
    url = pathlib.Path(filepath).as_uri()
    return (filepath, url)

def get_greeting(time):
    if time.hour >= 3 and time.hour <= 11:
        return "Guten Morgen."
    if time.hour > 11 and time.hour < 18:
        return "Guten Tag."
    return "Gute Nacht."

def get_actualtime(language, fuzzy=True, withDate=False, longDate=False):
    now = datetime.now()
    return get_time(now, language, fuzzy, withDate, longDate)

def get_time(theTime, language, fuzzy=True, withDate=False, longDate=False):
    logging.debug(theTime)
    locale.setlocale(locale.LC_ALL, locale.locale_alias[language])
    currentTime = theTime.strftime("%H:%M" if not withDate else "%A der %d. %B %Y, %H:%M" if longDate else "der %d.%m.%Y, %H:%M") if not fuzzy else fuzzyTime.get_fuzzy_time(theTime)
    logging.debug(f"get_time(currentTime={currentTime})")
    text = f"Es ist {currentTime}."
    return (theTime, text)
    
def say_time(language, fuzzy=True, withDate=False):
    theTime, text = get_actualtime(language, fuzzy, withDate)
    logging.debug(f"say_time(language={language}): {text}")
    return say(text, language)

def say_time_with_greeting(language):
    theTime, timeText = get_actualtime(language)
    greeting = get_greeting(theTime)
    text = f"{greeting}. {timeText}"
    return say(text, language)

class MetaMessage(type):
    def __getitem__(cls,key):
        logging.debug(f"__getitem__(key={key}, {type(key)})")
        if int(key) < len(Message.Files):
            filepath = os.path.join(Message.Directory,Message.Files[int(key)])
        else:
            raise IndexError()

        return pathlib.Path(filepath).as_uri()
    
class Message(object, metaclass=MetaMessage):
    class Key(Enum):
        
        UnknownError = 0, 'Unkown'
        NoInternet = 1, 'No internet'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member._fullname_ = name
            return member
        
        def __int__(self):
            return self.value
        
    Files = ["unknown_error.mp3", "no_internet.mp3"]
    Directory = "/var/radio/messages"


def recordMessage(message):
    testClass = TestClass()
    
    filepath, url = say(message, "de")
    testClass.radioPlayer().playUrl(url, True)
    response = input("Soll die Audio-Datei gelöscht werden? ")
    if response.lower() == "ja":
        os.remove(filepath)
    else:
        filename = input("Bitte den Dateinamen für die Zieldatei eingeben: ")
        os.rename(filepath, os.path.join(Message.Directory, filename))

def testMessageFiles():
    for key in Message.Key:
        uri = Message[key]
        filepath = urllib.parse.urlparse(uri).path        
        logging.debug(f"uri({uri})=path({filepath}) {'exists' if os.path.exists(filepath) else 'does not exist'}")
    
class TestError(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class TestClass:
    def __init__(self):
        self._radioPlayer = RadioPlayer.RadioPlayer("/var/radio/conf/radio.json")
        self._radioPlayer.setVolume(75)
        self._theTime = datetime(2024,2, 22, 14, 18)

    @staticmethod
    def AssertEqual(expected, actual):
        if expected != actual:
            raise TestError(f"expected result {expected} does not  match the actual result {actual}")

    def radioPlayer(self):
        return self._radioPlayer
    
    def testLocale(self):
        
        for lang in ['de', 'de_DE', 'es', 'es_ES']:
            try:
                logging.debug(f"testLocale(lang={lang})")
                if lang in locale.locale_alias:
                    locale.setlocale(locale.LC_ALL, locale.locale_alias[lang])
                else:
                    logging.debug(f"{lang} is not in locale.locale_alias")
            except Exception as e:
                logging.error(e)
 
    def _testTime(self, fuzzy, withDate = False):
        filepath, url = say_time('de', fuzzy,withDate)
        self._radioPlayer.playUrl(url, True)
        os.remove(filepath)

    def testFuzzyTime(self):
        self._testTime(True)
        
    def testWithoutFuzzyTime(self):
        self._testTime(False)

    def testDate(self):
        self._testTime(False, True)

    def testSayTimeWithGreeting(self):
        filepath, url = say_time_with_greeting('de')
        logging.debug(f"{filepath}, {url}")

    def run(self):
        self.testClass.testLocale()
        self.testClass.testFuzzyTime()
        self.testClass.testWithoutFuzzyTime()
        self.testClass.testDate()
        self.testClass.testSayTimeWithGreeting()

        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    
    testMessageFiles()
