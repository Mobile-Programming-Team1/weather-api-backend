from datetime import datetime, timedelta, timezone
from timezonefinder import TimezoneFinder
from dateutil.relativedelta import relativedelta
import pytz


def convert_to_kst_date(utc_timestamp: int) -> str:
    # UNIX timestamp → UTC → KST → 날짜 문자열
    dt_utc = datetime.utcfromtimestamp(utc_timestamp)
    dt_kst = dt_utc + timedelta(hours=9)
    return dt_kst.strftime("%Y-%m-%d")


def extract_daily_forecast(city: str, data: dict):
    return {
        "city": city,
        "forecast": [
            {
                "date": day["date"],
                "weather": day["weather"]
            }
            for day in data
        ]
    }


# start_date부터 end_date까지의 timestamp 리스트 반환
# date_str 포맷: yyyyMMdd (ex: 20210102 - 2021년 1월 2일일)
# offset hour를 통해 도시 별로 정오에 해당하는 UTC Timestamp로 변환환
def get_local_noon_utc_timestamps(start_date_str: str, end_date_str: str, offset_hours: int):
    # 지정한 오프셋을 기반으로 시간대 생성
    local_tz = timezone(timedelta(hours=offset_hours))

    # 시작/종료일을 해당 시간대의 정오로 지정
    start_date = datetime.strptime(start_date_str, "%Y%m%d").replace(hour=12, tzinfo=local_tz)
    end_date = datetime.strptime(end_date_str, "%Y%m%d").replace(hour=12, tzinfo=local_tz)

    # 날짜 수만큼 UTC 타임스탬프 리스트 생성
    delta = end_date - start_date
    return [
        int((start_date + timedelta(days=i)).astimezone(timezone.utc).timestamp())
        for i in range(delta.days + 1)
    ]


def get_coordinates_by_city_name(city_name: str, cities_data: list):
    for city in cities_data:
        if city["name"].lower() == city_name.lower():
            return {"lat": city["lat"], "lon": city["lon"]}
    raise ValueError(f"도시 이름 '{city_name}'을 찾을 수 없습니다.")



def get_utc_offset(city_lat, city_lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=city_lat, lng=city_lon)
    if not tz_name:
        raise ValueError("해당 좌표에 대한 타임존을 찾을 수 없습니다.")

    tz = pytz.timezone(tz_name)
    now = datetime.utcnow()
    offset = tz.utcoffset(now)

    return offset.total_seconds() // 3600  # 시간 단위로 반환

def get_current_utc_timestamp():
    return int(datetime.now(timezone.utc).timestamp())

def get_future_utc_timestamp(days):
    future = datetime.now(timezone.utc) + timedelta(days=4)
    return int(future.timestamp())


def one_year_ago_timestamp(timestamp: int) -> int:
    dt = datetime.utcfromtimestamp(timestamp)
    one_year_ago = dt - relativedelta(years=1)
    return int(one_year_ago.timestamp())