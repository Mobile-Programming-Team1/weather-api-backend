from pydantic import BaseModel


class DailyWeather(BaseModel):
    date: str
    weather: str

class City(BaseModel):
    name: str
    country: str
    lon: float
    lat: float

class DailyAir(BaseModel):
    date: str
    air: int # 1 ~ 5까지 (1이 매우 좋음. 5가 매우 나쁨)

class RecommCityResponse(BaseModel):
    date: str
    weather: str
    list: list[str]

class StatusResponse(BaseModel):
    status: str

class WeatherResponse(BaseModel):
    city: str
    forecast: list[DailyWeather]

class AirResponse(BaseModel):
    city: str
    list: list[DailyAir]

class CitiesResponse(BaseModel):
    cities: list[City]