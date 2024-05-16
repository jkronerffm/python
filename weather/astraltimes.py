from astral import LocationInfo
from astral.moon import moonrise, moonset, phase
from astral.sun import sun, daylight
from astral.location import Location
from astral.geocoder import group, database, add_locations, lookup
from enum import Enum
from datetime import datetime, timedelta
import logging
from area import Area

MoonPhase_transcription = {
    'en': ['new moon', 'first quarter', 'waxing crescend', 'waxing gibbous',
           'full moon', 'waning gibbous', 'waning crescend', 'last quarter'],
    'de': ['Neumond', 'zunehmender Sichelmond', 'zunehmender Halbmond',  'zunehmender Dreiviertelmond',
           'Vollmond', 'abnehmender Dreiviertelmond', 'abnehmender Halbmond', 'abnehmender Sichelmond'],
    'es': ['luna nueva', 'luna creciente creciente', 'luna creciente', 'cuarto creciente de luna',
           'luna llena', 'cuarto menguante de luna', 'luna creciente menguante', 'luna creciente menguante']
}

# This enum references the moon phases from new moon(0) over full moon(4) to the last quarter of moon(7)
class MoonPhase(Enum):
    New_Moon = 0
    First_Quarter = 1
    Waxing_Crescend = 2
    Waxing_Gibbous = 3
    Full_Moon = 4
    Waning_Gibbous = 5
    Waning_Crescend = 6
    Last_Quarter = 7


    def get_transcription(self, lang):
        if not (lang in (MoonPhase_transcription)):
            raise KeyError("Language not found in transcription!")

        if len(MoonPhase_transcription[lang]) < self.value:
            raise IndexError("Transcription does not contain requested index")
        
        return MoonPhase_transcription[lang][self.value]


class AstralCalculator:
    def __init__(self, area, day):
        self._locationInfo = LocationInfo(area.city(), area.country(), area.timezone(), area.latitude(), area.longitude())
        self._myCity = Location(self._locationInfo)
        self._day = day

    def _date(self):
        return datetime(self._day.year, self._day.month, self._day.day)

    def _tzinfo(self):
        return self._myCity.timezone

    def _observer(self):
        return self._locationInfo.observer

    def get_suntimes(self):
        logging.debug(f"{self.__class__.__name__}.get_suntimes()")
        observer = self._observer()
        date = self._date()
        tzinfo = self._tzinfo()
        s = sun(observer, date= date, tzinfo = tzinfo)
        result = s
        return result

    @staticmethod
    #result :
    #     0 -> New_Moon        0
    #  1- 4 -> First_Quarter   1
    #  5- 9 -> Waxing_Crescend 2
    # 10-13 -> Waxing_Gibbous  3
    #    14 -> Full_Moon       4
    # 15-18 -> Waning_Gibbous  5
    # 19-23 -> Waning_Crescend 6
    # 24-27 -> Last_Quarter    7
    def get_moon_phase(phase):
        p = int(phase)
        if p == 0:
            return MoonPhase(0)
        elif p in range(1,5):
            return MoonPhase(1)
        elif p in range(5,10):
            return MoonPhase(2)
        elif p in range(10, 14):
            return MoonPhase(3)
        elif p == 14:
            return MoonPhase(4)
        elif p in range(15, 19):
            return MoonPhase(5)
        elif p in range(19, 24):
            return MoonPhase(6)
        else:
            return MoonPhase(7)
        
    def get_moontimes(self, lang = 'de'):
        tzinfo = self._tzinfo()
        mr = moonrise(self._observer(), date = self._date(), tzinfo = tzinfo)
        ms = moonset(self._observer(), date = self._date(), tzinfo = tzinfo)
        p = int(phase(self._date()))
        result = {
            'phase': AstralCalculator.get_moon_phase(p).get_transcription(lang),
            'moonrise': mr,
            'moonset': ms
        }

        return result
            
    def get_degrees(value):
        dg = math.trunc(value)
        sec = round((value - dg)*60,10)
        return f"{dg}°{sec}'"

    def get_Location(latitude, longitude):
        return f"{get_degrees(latitude)}N,{get_degrees(longitude)}E"

def get_localArea():
    latitude=50.11
    longitude=8.68
    area = Area(city = "Frankfurt am Main",
                country = "Deutschland",
                timezone = "Europe/Berlin",
                latitude=latitude, longitude=longitude)
    return area

def test_AstralCalculator(area):
    now =datetime.now()
    astralCalculator = AstralCalculator(area, now)
    suntime = astralCalculator.get_suntimes()
    for key, value in suntime.items():
        print(f"{key:10s}: {value}")
    moontime = astralCalculator.get_moontimes()
    for key, value in moontime.items():
        print(f"{key:10s}: {value}")

def test_astralSun(area):
    import astral.sun
    from datetime import tzinfo
    locationInfo = LocationInfo(area.city(), area.country(), area.timezone(), area.latitude(), area.longitude())
    myCity = Location(locationInfo)
    sunValues = sun(myCity.observer, datetime.now())
    for key, value in sunValues.items():
        print(f"{key:10s}: {value.astimezone(None)}")

    v = daylight(myCity.observer, datetime.now())
    julianday = astral.sun.julianday(datetime.now())
    juliancentury= astral.sun.julianday_to_juliancentury(julianday)
    zenith = astral.sun.zenith(myCity.observer, datetime.now(locationInfo.tzinfo))
    elevation = astral.sun.elevation(myCity.observer, datetime(2024,3,26,6,30,0,tzinfo=locationInfo.tzinfo))
    azimuth = astral.sun.azimuth(myCity.observer, datetime(2024,3,26,6,30,0,tzinfo=locationInfo.tzinfo))
    sun_declination = astral.sun.sun_declination(juliancentury)
    time_of_transit = astral.sun.time_of_transit(myCity.observer, datetime.now(locationInfo.tzinfo), zenith,direction=astral.sun.SunDirection.RISING)
    zenith_and_azimuth = astral.sun.zenith_and_azimuth(myCity.observer, datetime.now(locationInfo.tzinfo))
    print(f"daylight: {v}")
    print(f"today: {astral.sun.today()}")
    print(f"julianday: {julianday}")
    print(f"juliancentury: {juliancentury}")
    print(f"eccentric_location_earth_orbit: {astral.sun.eccentric_location_earth_orbit(juliancentury)}")
    print(f"elevation: {elevation}, azimuth: {azimuth}")
    print(f"zenith: {zenith}")
    print(f"zenith_and_azimuth: {zenith_and_azimuth}")
    print(f"refraction_at_zenith: {astral.sun.refraction_at_zenith(zenith)}")
    print(f"sun_declination: {sun_declination}")
    print(f"time_of_transit: {time_of_transit}")
    print(dir(astral.sun))

def test_elevation_and_azimuth(area):
    import astral.sun
    locationInfo = LocationInfo(area.city(), area.country(), area.timezone(), area.latitude(), area.longitude())
    location = Location(locationInfo)
    observer = location.observer
    tzinfo = locationInfo.tzinfo
    for h in range(0,24):
        dt = datetime(2026, 3, 26, h, 0, 0, 0, tzinfo)
        elevation = astral.sun.elevation(observer, dt)
        azimuth = astral.sun.azimuth(observer, dt)
        print(f"{dt}|{elevation:10.2f}|{azimuth:10.2f}")

    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    area = get_localArea()
    test_elevation_and_azimuth(area)
    test_astralSun(area)
