import os
import sys
root = os.path.dirname(os.getcwd())
sys.path.append(root)
sys.path.append(os.path.join(root, "weather"))
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
#from WeatherCalculator import WeatherCalculator as Weatherman
from area import Area
import asyncio
import queue
from threading import Lock
def play(filepath, blocking = False):
    global radioPlayer
    radioPlayer.playUrl(filepath, blocking)
    
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

def test_func():
    path = "/var/radio/wakeup"
    statementList = []
    statementList += ["Ja, hallo erstmal."]
    statementList += ["Ich weiß nicht, ob Du's schon wusstest, aber ich bin Dein freundlicher Wecker."]
    statementList += ["Jetzt haben wir gerade die Zeit erreicht, die Du für heute eingestellt hast."]
    statementList += ["Bleibe also besser nicht länger im Bett liegen, sondern bewege erst Dein linkes und dein rechtes Bein und dann den Rest deines Körpers aus dem Bett."]
    statementList += ["Ich wünsche Dir einen schönen Tag"]
    itemList = []
    for index, statement in enumerate(statementList):
        filename, url = say(statement, "de")
        basename, extension = os.path.splitext(filename)
        destpath = os.path.join(path, f"item_{index:02}{extension}")
        os.rename(filename, destpath)
        itemList.append(destpath)
    with open(os.path.join(path, "statement.m3u"), "w") as outfile:
        outfile.write("\n".join(str(item) for item in itemList))

async def produce_multipleLineOutput(sentences, lang, q):
    logging.debug("produce_multipleLineOutput()")
    for sentence in sentences:
        logging.debug(f">>> {sentence}")
        (filename, url) = say(sentence, lang)
        await asyncio.sleep(0.5)
        logging.debug(f">>> {filename}, {url}")
        q.put((filename, url))
    logging.debug("produce_multipleOutput(): after the loop")
    await asyncio.sleep(0.5)
    q.join()
    logging.debug("produce_multi0leOutput(): processing the audio files is done")
    loop = asyncio.get_running_loop()
    logging.debug("produce_multipleLineOutput() is done")
    return len(sentences)
    
async def consume_multipleLineOutput(q, len_of_sentences, radioPlayer):
    logging.debug("consume_multipleLineOutput()")
    number_of_sentence = 0
    while number_of_sentence < len_of_sentences:
        await asyncio.sleep(0.5)
        (filename, url) = q.get()
        logging.debug(f"consume_multipleLineOutput(url={url}) play file")
        radioPlayer.playUrl(url, blocking=True)
        logging.debug(f"consume_multipleLineOutput(filename={filename}) delete file")
        os.remove(filename)
        q.task_done()
        number_of_sentence+= 1
    logging.debug("consume_multipleLineOutput() is done")
    return number_of_sentence

async def say_multipleLineOutput(sentences, lang, radioPlayer):
    logging.debug("say_multipleLineOutput()")
    q = queue.Queue()
    res = await asyncio.gather(produce_multipleLineOutput(sentences, lang, q), consume_multipleLineOutput(q, len(sentences), radioPlayer))
    logging.debug(f"say_multipleLineOutput: result is {res}")
    
def test_multipleLineOutput():
    sentences = []
    sentences += ["Ja, hallo erstmal."]
    sentences += ["Ich weiß nicht, ob Du's schon wusstest, aber ich bin Dein freundlicher Wecker."]
    sentences += ["Jetzt haben wir gerade die Zeit erreicht, die Du für heute eingestellt hast."]
    sentences += ["Bleibe also besser nicht länger im Bett liegen, sondern bewege erst Dein linkes und dein rechtes Bein und dann den Rest deines Körpers aus dem Bett."]
    sentences += ["Ich wünsche Dir einen schönen Tag"]
    asyncio.run(say_multipleLineOutput(sentences, "de"))

def test_weatherOutput():
    area = Area(city = "Frankfurt am Main",
                country = "Germany",
                timezone = "Europe/Berlin",
                latitude = 50.11,
                longitude = 8.68)
    
    weatherman = Weatherman(area, None)
    freeSpeechForecast = Weatherman.HumanUnderstandableStatement(weatherman.run())
    asyncio.run(say_multipleLineOutput(freeSpeechForecast, "de"))
    
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer.RadioPlayer("/var/radio/conf/radio.json")
    test_weatherOutput()
    ##testMessageFiles()
