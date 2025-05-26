

from fastapi import APIRouter, HTTPException
import httpx
from ..model import AirResponse
from ..environ import OPENWEATHER_API_KEY
from ..loader import CITIES_DATA
from .util import get_local_noon_utc_timestamps, convert_to_kst_date, get_coordinates_by_city_name, get_utc_offset, get_noon_utc_timestamp, get_first_last_with_length
from .util import one_year_after_timestamp_tz, one_year_ago_timestamp_tz, get_timezone, get_future_utc_timestamp_from, split_sorted_list_bisect

router = APIRouter()

@router.post("/air/", response_model=AirResponse)
async def get_air(city: str, start_date: str, end_date: str):

    try:
        client = httpx.AsyncClient(timeout=30.0)
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine"

        # 제공된 도시 이름에 해당하는 lon, lat 정보 가져오기기
        city_location = get_coordinates_by_city_name(city, CITIES_DATA)
        
        city_utc_offset =  int(get_utc_offset(city_location["lat"], city_location["lon"]))
        city_timezone= get_timezone(city_location["lat"], city_location["lon"])
        # 각 날짜마다 정오의 Timestamp로 변환
        timestamps = get_local_noon_utc_timestamps(start_date, end_date, city_utc_offset)
        if(len(timestamps) > 10):
            raise HTTPException(status_code=400, detail="조회 기간이 너무 깁니다")

        data_all = []
        # 오늘의 UTC timestamp
        today_noon_utc = get_noon_utc_timestamp(city_utc_offset)

        print("today_noon_utc", today_noon_utc)

        # 1. history data가 필요한 경우 (오늘 이전인 경우) - 4일 이내의 경우
        # 2. 4일 이후인 경우
        utc_before, utc_after = split_sorted_list_bisect(timestamps, get_future_utc_timestamp_from(today_noon_utc, 5, "days"))
        print("utc_before", utc_before)
        print("utc_after", utc_after)

        # 4일 이후의 정오 TimeStamp - A를 구한다.
        # timestamps를 A이하와 A 초과로 구분한다.
        # A이하에서 구한 data를 정오만 filtering한다.
        # A초과에서 구한 data를 정오만 filtering한다.

        # 각 Timestamp마다 API 호출 + 결과를 data_all에 저장
        start, end = get_first_last_with_length(utc_before)
        print("start", start)
        print("end", end)

        if(start and end != None):
            data =  await fetch_from_history(client, city_location, start, end)

            for datum in data["list"]:
                if datum["dt"] in utc_before:
                    data_all.append({
                        "date": convert_to_kst_date(datum["dt"]),
                        "air": datum["main"]["aqi"]
                    })

        # utc_after를 일년전 timestamp로 변환환
        utc_after = [one_year_ago_timestamp_tz(timestamp, city_timezone) for timestamp in utc_after]
        start, end = get_first_last_with_length(utc_after)
        print("after_start", start)
        print("after_end", end)

        if(start and end != None):
            data =  await fetch_from_history(client, city_location, start, end)

            for datum in data["list"]:
                if datum["dt"] in utc_after:
                    data_all.append({
                        "date": convert_to_kst_date(one_year_after_timestamp_tz(datum["dt"], city_timezone)),
                        "air": datum["main"]["aqi"]
                    })



        # data_all을 반환 타입에 맞게 변환환
        return extract_air_response(city, data_all)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    


async def fetch_from_history(client, city_location, start, end):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": city_location["lat"],
        "lon": city_location["lon"],
        "start": start,
        "end": end,
        "appid": OPENWEATHER_API_KEY,
    }
    print(f'url: {url}?lat={city_location["lat"]}&lon={city_location["lon"]}&start={start}&end={end}&appid={OPENWEATHER_API_KEY}')
        
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