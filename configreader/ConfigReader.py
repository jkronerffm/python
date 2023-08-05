import xmltodict
import json
import pathlib
import configparser
import logging
import csv
import datetime
import dateutil.parser as DateParser

logger = logging.getLogger("configreader")

class SuffixNotFoundError(Exception):
    ""
    pass

class ConfigReader:
    Accept = None
    
    def __init__(self):
        self._suffixes={'xml': ['.xml'], 'json': ['.json'], 'ini': ['.ini'], 'csv': ['.csv']}
        self._mapping={'xml': self.readXml, 'json': self.readJson, 'ini': self.readIni, 'csv': self.readCsv}

    def _getIdent(self, suffix):
        for (ident, suffixes) in self._suffixes.items():
            if suffix in suffixes:
                return ident
        raise SuffixNotFoundError()

    def addSuffix(self, fileType, suffix):
        if not (fileType in self._suffixes.keys()):
            self._suffixes.update({fileType: [suffix]})
        else:
            self._suffixes[fileType] += suffix
            
    def read(self, filepath) -> dict:
        suffix=pathlib.Path(filepath).suffix.lower()
        ident = self._getIdent(suffix)
        return self._mapping[ident](filepath)

    def readXml(self, filepath):
        return xmltodict.parse(pathlib.Path(filepath).read_text())

    def readJson(self, filepath):
        with open(filepath) as fp:
            return json.load(fp)

    def readIni(self, filepath):
        iniFile = configparser.ConfigParser()
        iniFile.read(filepath)
        return iniFile._sections

    def readCsv(self, filepath):
        logger.debug("(filepath=\"%s\")" %(filepath))
        with open(filepath,encoding="utf-8-sig") as fp:
            csvReader = csv.DictReader(fp)
            content = []
            addedRows=0
            for row in csvReader:
                if ConfigReader.Accept != None and ConfigReader.Accept(row):
                    addedRows+= 1
                    content.append(
                        {
                            'Subject': row['Subject'],
                            'Start Date': row['Start Date'],
                            'End Date': row['End Date'],
                            'Start Time': row['Start Time']
                        })
            logger.debug("(): added %d rows" % (addedRows))
            content.sort(key=lambda item: DateParser.parse(item['Start Date'],dayfirst=True))
            return content
            
def accept(content):
    accepted = True
    conditions = {
        "Start Date": lambda content, k:
            DateParser.parse(content[k],dayfirst=True).date() >= datetime.datetime.now().date() or DateParser.parse(content["End Date"],dayfirst=True).date() >= datetime.datetime.now().date(),
        "Required Attendees": lambda  content, k: "Cydonia" in content[k]
    }
    for (key, condition) in conditions.items():
        accepted = accepted and condition(content, key)
    return accepted

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s %(message)s")
    configReader = ConfigReader()
    configXml = configReader.read("config.xml")
    print("from xml file: %s" % (str(configXml)))
    configJson = configReader.read("config.json")
    print("from json file: %s" % (str(configJson)))
    configIni = configReader.read("config.ini")
    print("from ini file: %s" % (str(configIni)))
    ConfigReader.Accept = accept
    configCsv = configReader.read("kalender.CSV")
    print("from csv file: %s" % (str(configCsv)))
