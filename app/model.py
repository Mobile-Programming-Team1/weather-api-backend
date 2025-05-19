from pydantic import BaseModel


class DailyWeather(BaseModel):
    date: str
    weather: str

class WeatherResponse(BaseModel):
    city: str
    forecast: list[DailyWeather]


class City(BaseModel):
    name: str
    country: str
    lon: float
    lat: float

class CitiesResponse(BaseModel):
    cities: list[City]