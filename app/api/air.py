

from fastapi import APIRouter, HTTPException
import httpx
from ..model import AirResponse
from ..environ import OPENWEATHER_API_KEY
from ..loader import CITIES_DATA
from .util import get_local_noon_utc_timestamps, convert_to_kst_date, get_coordinates_by_city_name, get_utc_offset
from .util import get_current_utc_timestamp, get_future_utc_timestamp, one_year_ago_timestamp, get_future_utc_timestamp_from

router = APIRouter()

@router.post("/air/", response_model=AirResponse)
async def get_weather(city: str, start_date: str, end_date: str):

    try:
        client = httpx.AsyncClient(timeout=30.0)
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine"

        # 제공된 도시 이름에 해당하는 lon, lat 정보 가져오기기
        city_location = get_coordinates_by_city_name(city, CITIES_DATA)
        
        # 각 날짜마다 정오의 Timestamp로 변환
        timestamps = get_local_noon_utc_timestamps(start_date, end_date, int(get_utc_offset(city_location["lat"], city_location["lon"])))
        if(len(timestamps) > 10):
            raise HTTPException(status_code=400, detail="조회 기간이 너무 깁니다")

        data_all = []

        # 1. history data가 필요한 경우 (오늘 이전인 경우)
        # 2. 오늘 이후인 경우
        # 2-1. 4일 이내인 경우
        # 2-2. 4일 이후인 경우

        # 각 Timestamp마다 API 호출 + 결과를 data_all에 저장
        for timestamp in timestamps:
            data = {}
            if(timestamp < get_current_utc_timestamp()):
                data = await fetch_from_history(client, city_location, timestamp)
            elif(timestamp > get_future_utc_timestamp(4, "days")):
                data = await fetch_from_forecast(client, city_location, timestamp)
            else:
                data = await fetch_from_history(client, url, city_location, one_year_ago_timestamp(timestamp))
            
            datum = data["list"][0]
            data_all.append({
                "date": convert_to_kst_date(datum["dt"]),
                "air": datum["main"]["aqi"]
            })

        # data_all을 반환 타입에 맞게 변환환
        return extract_air_response(city, data_all)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    

async def fetch_from_history(client, city_location, timestamp):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": city_location["lat"],
        "lon": city_location["lon"],
        "start": timestamp,
        "end": timestamp,
        "appid": OPENWEATHER_API_KEY,
    }
        
    response = await client.get(url, params=params)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
    return response.json()


async def fetch_from_forecast(client, city_location, timestamp):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": city_location["lat"],
        "lon": city_location["lon"],
        "start": timestamp,
        "end": get_future_utc_timestamp_from(timestamp, 1),
        "appid": OPENWEATHER_API_KEY,
    }
        
    response = await client.get(url, params=params)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
    return response.json()


def extract_air_response(city: str, data: dict):
    return {
        "city": city,
        "list": [
            {
                "date": day["date"],
                "air": day["air"]
            }
            for day in data
        ]
    }