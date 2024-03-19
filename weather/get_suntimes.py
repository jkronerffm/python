from suntime import Sun
from suntimes import SunTimes
from astral import LocationInfo
from astral.moon import moonrise
from astral.sun import sun
from astral.location import Location
from astral.geocoder import group, database, add_locations, lookup

from datetime import datetime, timedelta
import pytz
import math
import logging
import inspect

def get_sunrise_by_Suntime(latitude, longitude, for_date= datetime.now(), tz_name="Europe/Berlin"):
    tz = pytz.timezone(tz_name)
    day = datetime(for_date.year, for_date.month, for_date.day)
    sun = Sun(latitude, longitude)
    sunrise = sun.get_sunrise_time(day, tz)
    sunset = sun.get_sunset_time(day, tz)
    print(20*"=" + " suntime.Sun " + 10*"=")
    print(f"sunrise for {day.strftime('%x')}: {sunrise.astimezone(tz)}")
    print(f"sunset  for {day.strftime('%x')}: {sunset.astimezone(tz)}")
    
def get_sunrise_by_SunTimes(latitude, longitude, altitude=0, for_date = datetime.now(), tz_name="Europe/Berlin"):
    sun = SunTimes(longitude=longitude, latitude=latitude, altitude=altitude)
    day = datetime(for_date.year, for_date.month, for_date.day)
    print(20*"=" + " suntimes.SunTimes " + 10*"=")
    print(sun.risewhere(day, tz_name))
    print(sun.setwhere(day, tz_name))
    logging.debug(f"{type(sun)} {dir(sun)}")
#    logging.debug(inspect.signature(sun.altitude))

def get_suntimes_by_astral(city, country, timezone, latitude, longitude, day):
    city = LocationInfo(city, country, timezone, latitude, longitude)
    myCity = Location(city)
    s = sun(city.observer, date = datetime(day.year, day.month, day.day), tzinfo = myCity.timezone)
    print(20*"=" + " astral " + 10 * "=")
    print(s['sunrise'])
    print(s['sunset'])

def get_moontime_by_astral(city, country, timezone, latitude, longitude, day):
    city = LocationInfo(city, country, timezone, latitude, longitude)
    myCity = Location(city)
    m = moonrise(city.observer, date = datetime(day.year, day.month, day.day))
    print(m)
        
def print_Keys(continent_name, db = None):
    if db == None:
        db = database()
    continent = group(continent_name, db)
    print(sorted(continent.keys()))
    return db

def get_degrees(value):
    dg = math.trunc(value)
    sec = round((value - dg)*60,10)
    return f"{dg}°{sec}'"

def get_Location(latitude, longitude):
    return f"{get_degrees(latitude)}N,{get_degrees(longitude)}E"

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    latitude=50.11
    longitude=8.68
    for for_date in [datetime.now(), datetime.now() + timedelta(days=1), datetime.now() + timedelta(days=2)]:
        get_sunrise_by_Suntime(latitude, longitude, for_date)
        get_sunrise_by_SunTimes(latitude, longitude, for_date=for_date)
        get_suntimes_by_astral("Frankfurt", "Deutschland", "Europe/Berlin", 50.11,8.68, for_date)
        get_moontime_by_astral("Frankfurt", "Deutschland", "Europe/Berlin", 50.11, 8.68, for_date)
    loc = get_Location(50.09,8.68)
    print(loc)
    db = database()
    add_locations(f"Frankfurt Sachsenhausen,europe,Europe/Berlin,{loc}", db)
    print(40*"#")
    place = lookup("Frankfurt Sachsenhausen", db)
    print(place)
    
    print_Keys("europe")
