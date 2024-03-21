
class Area:
    def __init__(self, city, country, timezone, latitude=None, longitude=None):
        self._city = city
        self._country = country
        self._latitude = latitude
        self._longitude = longitude
        self._timezone = timezone

    def city(self):
        return self._city

    def coordinates(self):
        return (self.latitude(), self.longitude())

    def country(self):
        return self._country

    def latitude(self):
        return self._latitude

    def longitude(self):
        return self._longitude

    def timezone(self):
        return self._timezone

    def set_city(self, value):
        self._city = value

    def set_country(self, value):
        self._country = value

    def set_latitude(self, value):
        self._latitude = value

    def set_longitude(self, value):
        self._longitude = value

    def set_timezone(self, value):
        self._timezone = value
