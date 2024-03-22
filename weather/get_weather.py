import os
import sys
root = os.path.dirname(os.getcwd())
sys.path.append(root)
from area import Area
from astraltimes import AstralCalculator
import python_weather
import asyncio
import locale
import logging
from dateutil import tz
import datetime
from datetime import timezone

class WeatherCalculator:
    def __init__(self, area, cb = None):
        self._area = area
        self._cb = cb
        
    def set_callback(cb):
        self._cb = cb
        
    def Fahrenheit_in_Celcius(grad_fahrenheit):
        grad_celcius = (grad_fahrenheit - 32) * 5/9
        return grad_celcius

    def translate(self,value):
        logging.debug(f"translate(value=<{type(value)}>{value})")
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

    def formatDate(self,date):
        locale.setlocale(locale.LC_TIME, 'de_DE')
        return date.strftime("%A, %d.%m.%Y")

    def _get_date(self, date):
        return datetime.datetime(date.year, date.month, date.day)

    def get_currentForecast(self, forecast):
        now = datetime.datetime.now()
        today = now.date()
        minValue = datetime.timedelta(hours = 24).total_seconds()
        result = None
        for hourlyForecast in forecast.hourly:
            timepoint = datetime.datetime.combine(today, hourlyForecast.time)
            d = (timepoint - now).total_seconds()
            if d < minValue:
                result = hourlyForecast
                minValue = d
            

        return result

    async def get_weather(self):
        async with python_weather.Client(unit=python_weather.METRIC, locale=python_weather.Locale.GERMAN) as client:
            weather = await client.get(self._area.city())
            try:
                date = weather.current.date
            except:
                date = datetime.datetime.now()
                
            sdate = self.formatDate(date)
            forecast = next(weather.forecasts)
            astralCalculator = AstralCalculator(self._area, date)
            currentForecast = self.get_currentForecast(forecast)
            suntimes = astralCalculator.get_suntimes()
            moon = astralCalculator.get_moontimes()
            result = {
                'date': sdate,
                'area': {
                    'city': weather.nearest_area.name,
                    'location': weather.location,
                    'region': weather.nearest_area.region
                },
                'current': {
                    'temperature': weather.current.temperature,
                    'description': self.translate(weather.current.description)
                },
                'forecast': {
                    'minTemperature': forecast.lowest_temperature,
                    'maxTemperature': forecast.highest_temperature,
                    'description': self.translate(currentForecast.description)
                },
                'sun': {
                    'rise': suntimes['sunrise'],
                    'set': suntimes['sunset']
                },
                'moon': {
                    'phase': self.translate(forecast.astronomy.moon_phase.name),
                    'rise': moon['moonrise'],
                    'set': moon['moonset']
                }
            }
                
            if self._cb != None:
                self._cb(result)
            return result

    def run(self):
        asyncio.run(self.get_weather())

    @staticmethod
    def HumanUnderstandableStatement(weather):
        l = [f"Die Außentemperatur beträgt jetzt {weather['current']['temperature']}°C.",
             f"Das Wetter ist jetzt {weather['current']['description']}.",
             f"Die Temperaturen werden heute zwischen {weather['forecast']['minTemperature']} und {weather['forecast']['maxTemperature']}°C liegen.",
             f"Die weiteren Aussichten für heute sind {weather['forecast']['description']}."
             ]
        return " ".join(l)
        
    
def weatherCallback(weather):
    print(f"weatherCallback(weather={weather})")
    print(WeatherCalculator.HumanUnderstandableStatement(weather))
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    area = Area(city = "Frankfurt am Main",
                country = "Germany",
                timezone = "Europe/Berlin",
                latitude = 50.11,
                longitude = 8.68)
    weatherCalculator = WeatherCalculator(area, weatherCallback)
    weatherCalculator.run()
    
