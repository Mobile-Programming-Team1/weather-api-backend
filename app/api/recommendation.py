# 인자 2
# 날씨 - 7가지 중 하나
# 날짜 - 형식 동일

# 리턴
# 리스트 [해당하는 도시]
import httpx
from fastapi import APIRouter, Query
from ..model import RecommCityResponse
from .util import get_coordinates_by_city_name, get_local_noon_utc_timestamps, get_utc_offset
from ..loader import CITIES_DATA
from .weather import fetch_from_timemachine
import logging

router = APIRouter()
recommend_cities = ["Busan", "Gwangju", "Daejeon", "Kyoto", "Barcelona", "Rome", "Sydney", "Paris"]

@router.get("/recommendation", response_model=RecommCityResponse)
async def get_recommend_cities(weather: str, date: str = Query(description="ex) 20250105")):
    client = httpx.AsyncClient(timeout=30.0)
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
    
    matching_cities = []
    weather_all = []

    for city in recommend_cities:
        city_location = get_coordinates_by_city_name(city, CITIES_DATA)
        timestamp = get_local_noon_utc_timestamps(date, date, int(get_utc_offset(city_location["lat"], city_location["lon"])))
        data = await fetch_from_timemachine(client, url, city_location, timestamp)
        weather_all.append(data["data"][0]["weather"][0]["main"])

        if(data["data"][0]["weather"][0]["main"] == weather):
            print(data)
            matching_cities.append(city)

    logging.info(weather_all)

    response = {
        "date": date,
        "weather": weather,
        "list": matching_cities
    }
    return response