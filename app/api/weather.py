from fastapi import APIRouter, HTTPException
import httpx
from ..model import WeatherResponse
from ..environ import OPENWEATHER_API_KEY
from ..loader import CITIES_DATA
from .util import extract_daily_forecast, get_local_noon_utc_timestamps, convert_to_kst_date, get_coordinates_by_city_name, get_utc_offset
from .util import get_current_utc_timestamp, get_future_utc_timestamp, one_year_ago_timestamp, get_timezone, one_year_after_timestamp_tz, one_year_ago_timestamp_tz
import logging

router = APIRouter()

@router.post("/weather/", response_model=WeatherResponse)
async def get_weather(city: str, start_date: str, end_date: str):
    logging.info(f'weather request: city = {city}, start_date = {start_date}, end_date = {end_date}')
    try:
        client = httpx.AsyncClient(timeout=30.0)
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine"

        # 제공된 도시 이름에 해당하는 lon, lat 정보 가져오기기
        city_location = get_coordinates_by_city_name(city, CITIES_DATA)
        city_timezone = get_timezone(city_location["lat"], city_location["lon"])
        # 각 날짜마다 정오의 Timestamp로 변환
        timestamps = get_local_noon_utc_timestamps(start_date, end_date, int(get_utc_offset(city_location["lat"], city_location["lon"])))
        if(len(timestamps) > 10):
            raise HTTPException(status_code=400, detail="조회 기간이 너무 깁니다")
        
        data_all = []
        # 각 Timestamp마다 API 호출 + 결과를 data_all에 저장
        for timestamp in timestamps:
            data = {}

            if(timestamp > get_future_utc_timestamp(4, "days")):
                timestamp = one_year_ago_timestamp_tz(timestamp, city_timezone)
            
            data = await fetch_from_timemachine(client, url, city_location, timestamp)
            
            data_all.append({
                "date": convert_to_kst_date(one_year_after_timestamp_tz(data["data"][0]["dt"])),
                "weather": data["data"][0]["weather"][0]["main"]
            })

        # data_all을 반환 타입에 맞게 변환환
        return extract_daily_forecast(city, data_all)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    

async def fetch_from_timemachine(client, url, city_location, timestamp):
    params = {
        "lat": city_location["lat"],
        "lon": city_location["lon"],
        "dt": timestamp,
        "appid": OPENWEATHER_API_KEY,
    }
        
    logging.info(f'url: {url}?lat={city_location["lat"]}&lon={city_location["lon"]}&dt={timestamp}&appid={OPENWEATHER_API_KEY}')


    response = await client.get(url, params=params)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
    return response.json()