import python_weather

import asyncio
import os
import locale
import logging
from suntime import Sun
from dateutil import tz
import datetime
from datetime import timezone

def Fahrenheit_in_Celcius(grad_fahrenheit):
    grad_celcius = (grad_fahrenheit - 32) * 5/9
    return grad_celcius

def translate(value):
    v = value.strip()
    translations= {
        'Cloudy': 'Bewölkt',
        'Partly Cloudy': 'Wolkig',
        'Clear': 'Klar',
        'Patchy rain nearby': 'Örtlich Regen',
        'Overcast': 'Bedeckt',
        'FIRST_QUARTER': 'Erstes Viertel',
        'FULL_MOON': 'Vollmond',
        'LAST_QUARTER': 'Letztes Viertel',
        'NEW_MOON': 'Neumond',
        'WANING_CRESCENT': 'Abnehmende Mondsichel',
        'WANING_GIBBOUS': 'Abnehmender Dreiviertelmond',
        'WAXING_CRESCENT': 'Zunehmende Mondsichel',
        'WAXING_GIBBOUS': 'Zunehmender Dreiviertelmond'
    }

    if v in translations.keys():
        return translations[v]
    else:
        return v

def formatDate(date):
    locale.setlocale(locale.LC_TIME, 'de_DE')
    return date.strftime("%A, %d.%m.%Y")

async def get_weather():
    async with python_weather.Client(unit=python_weather.METRIC, locale=python_weather.Locale.GERMAN) as client:
        weather = await client.get('Frankfurt am Main')
        sdate = formatDate(weather.current.date)
        logging.debug(20*"-" + f" client.get returns <{type(weather)}> " + 20*"-")
        logging.debug(f"  {dir(weather)}")
        logging.debug(20*"-" + f" {type(weather)}.current=<{type(weather.current)}> " + 20*"-")
        logging.debug(f"  {dir(weather.current)}")
        print(f"Datum: {sdate}")
        print(f"{weather.nearest_area.name}(){weather.location}, {weather.nearest_area.region}")
        print("aktuell:")
        print(f"  {weather.current.temperature}°C, {translate(weather.current.description)}")
        for forecast in weather.forecasts:
            logging.debug(20*"-" + f" {type(forecast)} " + 20 * "-")
            logging.debug(f"  {dir(forecast)}")
            logging.debug(20*"-" + f" {type(forecast.astronomy)} " + 20 * "-")
            logging.debug(f"  {dir(forecast.astronomy)}")
            print(f"Datum: {formatDate(forecast.date)}")
            print(f"  Mondphase: {translate(forecast.astronomy.moon_phase.name)}, {forecast.astronomy.moon_phase.emoji}")
            print(f"  Mondaufgang: {forecast.astronomy.moon_rise}")
            print(f"  Monduntergang: {forecast.astronomy.moon_set}")
            if forecast.astronomy.sun_rise == None:
                sun = Sun(weather.location[0], weather.location[1])
                logging.debug(f"loctaion: {weather.location}")
                tz = timezone(datetime.timedelta(1/24))
                logging.debug(f"timezone: <{type(tz)}> {tz}")
                today_sr, today_ss = sun.get_sunrise_time(forecast.date,tz), sun.get_sunset_time(forecast.date,tz)
            else:
                today_sr, today_ss = forecast.astronomy.sun_rise, forecast.astronomy.sun_set
            print(f"  Sonnenaufgang: {today_sr}")
            print(f"  Sonnenuntergang: {today_ss}")
            print(f"  Temperatur: {forecast.lowest_temperature}°C - {forecast.highest_temperature}°C")
            for hourly in forecast.hourly:
                print(f'  --> {hourly.time}, T={hourly.temperature}°C, {translate(hourly.description)}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(get_weather())
