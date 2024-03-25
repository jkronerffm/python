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
            d = abs((timepoint - now).total_seconds())
            if d < minValue:
                result = hourlyForecast
                minValue = d
            

        return result

    @staticmethod
    def translate_windDirection(value, lang='de'):
        result = ""
        values = str(value).split(' ')
        direction = [
            {
                'en': 'north',
                'de': 'Nord',
                'es': 'norte'
            },
            {
                'en': 'northeast',
                'de': 'Nordost',
                'es': 'noreste'
            },
            {
                'en': 'east',
                'de': 'Ost',
                'es': 'este'
            },
            {
                'en': 'southeast',
                'de': 'Südost',
                'es': 'sureste'
            },
            {
                'en': 'south',
                'de': 'Süd',
                'es': 'sur'
            },
            {
                'en': 'southwest',
                'de': 'Südwest',
                'es': 'suroeste'
            },
            {
                'en': 'west',
                'de': 'West',
                'es': 'oeste'
            },
            {
                'en': 'northwest',
                'de': 'Nordwest',
                'es': 'noroeste'
            }
        ]
        for v in values:
            translation = next(d for d in direction if d['en'].casefold() == v.casefold())
            if not (lang in translation):
                raise KeyError('Requested language is not in translations')

            if len(result) > 0:
                result+= " "
            result += translation[lang]
            
        return result
    
    @staticmethod
    def get_windStrength(value):
        windStrength = None
        windSpeedToStrength = [
            {
                'speed': lambda speed : speed == 0,
                'strength': 0,
                'description': 'Windstille'
            },
            {
                'speed': lambda speed : speed <= 6,
                'strength': 1,
                'description': 'leiser Zug'
            },
            {
                'speed': lambda speed : speed >= 7  and speed <= 11,
                'strength': 2,
                'description': 'leichte Brise'
            },
            {
                'speed': lambda speed: speed >= 12 and speed <= 18,
                'strength': 3,
                'description': 'schwache Brise'
            },
            {
                'speed': lambda speed : speed >= 19 and speed <= 25,
                'strength': 4,
                'description': 'mäßiger Wind'
            },
            {
                'speed': lambda speed : speed >= 26 and speed <= 35,
                'strength': 5,
                'description': 'frischer Wind' 
            },
            {
                'speed': lambda speed : speed >= 36 and speed <= 46,
                'strength': 6,
                'description': 'starker Wind'
            },
            {
                'speed': lambda speed: speed >= 47 and speed <= 61,
                'strength': 7,
                'description': 'steifer Wind'
            },
            {
                'speed': lambda speed: speed >= 62 and speed <=72,
                'strength': 8,
                'description': 'stürmischer Wind'
            },
            {
                'speed': lambda speed: speed >= 73 and speed <= 86,
                'strength': 9,
                'description': 'Sturm'
            },
            {
                'speed': lambda speed: speed >= 87 and speed <= 100,
                'strength': 10,
                'description': 'schwerer Sturm'
            },
            {
                'speed': lambda speed: speed >= 101 and speed <= 15,
                'strength': 11,
                'description': 'orkanartiger Sturm',
            },
            {
                'speed': lambda speed: speed >= 118,
                'strength': 12,
                'description': 'Orkan'
            }
        ]
        windStrength = [w for w in windSpeedToStrength if w['speed'](value)]
        return windStrength[0]

    @staticmethod
    def get_windStrengthAsSentence(when, windStrength, direction):
        strength = windStrength['strength']
        description = windStrength['description']
        if strength == 0:
            result = f"{when} ist es {description}."
        else:
            result = f"Aus {direction}"
            if strength < 6:
                result += " weht"
            else:
                result += " bläst"
            result += f" {when}" 
            if strength == 1 or strength >= 4:
                result += " ein"
            else:
                result += " eine"
            result += f" {description}."
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
            windDirection = WeatherCalculator.translate_windDirection(currentForecast.wind_direction)
            suntimes = astralCalculator.get_suntimes()
            moon = astralCalculator.get_moontimes()
            windStrength = WeatherCalculator.get_windStrength(weather.current.wind_speed)
            result = {
                'date': sdate,
                'area': {
                    'city': weather.nearest_area.name,
                    'location': weather.location,
                    'region': weather.nearest_area.region
                },
                'current': {
                    'temperature': weather.current.temperature,
                    'description': self.translate(weather.current.description),
                    'windStrength': WeatherCalculator.get_windStrength(weather.current.wind_speed),
                    'windDirection': WeatherCalculator.translate_windDirection(weather.current.wind_direction),
                    'feelsLike': weather.current.feels_like
                },
                'forecast': {
                    'minTemperature': forecast.lowest_temperature,
                    'maxTemperature': forecast.highest_temperature,
                    'description': self.translate(currentForecast.description),
                    'feelsLike': currentForecast.feels_like,
                    'windStrength': WeatherCalculator.get_windStrength(currentForecast.wind_speed),
                    'windDirection': WeatherCalculator.translate_windDirection(currentForecast.wind_direction)
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
             f"Das fühlt sich an wie {weather['current']['feelsLike']}°C." if weather['current']['temperature'] != weather['current']['feelsLike'] else "",
             f"Das Wetter ist {weather['current']['description']}.",
             WeatherCalculator.get_windStrengthAsSentence('', weather['current']['windStrength'], weather['current']['windDirection']),
             f"Die Temperaturen werden heute zwischen {weather['forecast']['minTemperature']} und {weather['forecast']['maxTemperature']}°C liegen.",
             f"Die weiteren Aussichten sind {weather['forecast']['description']}."
             ]
        return " ".join(l)
        
def weatherCallback(weather):
    logging.debug(f"weatherCallback(weather={weather})")
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
    
