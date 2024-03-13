import python_weather

import asyncio
import os
import locale

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
    async with python_weather.Client(unit=python_weather.IMPERIAL, locale=python_weather.Locale.GERMAN) as client:
        weather = await client.get('Frankfurt am Main', unit=python_weather.METRIC)
#        locale.setlocale(locale.LC_TIME, 'de_DE')
        sdate = formatDate(weather.current.date)
        print(f"Datum: {sdate}")
        print(f"{weather.nearest_area.name}, {weather.nearest_area.region}")
        print("aktuell:")
        print(f"  {weather.current.temperature}°C, {translate(weather.current.description)}")
        for forecast in weather.forecasts:
            print(f"Datum: {formatDate(forecast.date)}")
            print(f"  Mondphase: {translate(forecast.astronomy.moon_phase.name)}")
##            print(f"  Mondaufgang: {forecast.astronomy}")
##            print(f"  Monduntergang: {forecast.astronomy.moon_set}")
            print(f"  Sonnenaufgang: {forecast.astronomy.sun_rise}")
            print(f"  Sonnenuntergang: {forecast.astronomy.sun_set}")
            print(f"  Temperatur: {forecast.lowest_temperature}°C - {forecast.highest_temperature}°C")
            for hourly in forecast.hourly:
                print(f'  --> {hourly.time}, T={hourly.temperature}°C, {translate(hourly.description)}')

if __name__ == "__main__":
    asyncio.run(get_weather())
