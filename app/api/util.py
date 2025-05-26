from datetime import datetime, timedelta, timezone
from timezonefinder import TimezoneFinder
from dateutil.relativedelta import relativedelta
import pytz
import bisect


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

def get_noon_utc_timestamp(offset_hours: int) -> int:
    """
    주어진 UTC offset에 따라 오늘의 정오(local time) 기준 UTC 타임스탬프를 반환
    :param offset_hours: 예) KST는 +9, EST는 -5
    :return: UTC timestamp (int)
    """
    # 현재 UTC 기준 날짜
    now_utc = datetime.utcnow()
    
    # offset을 고려한 현재 지역 날짜
    local_today = now_utc + timedelta(hours=offset_hours)
    local_noon = datetime(
        year=local_today.year,
        month=local_today.month,
        day=local_today.day,
        hour=12, minute=0, second=0
    )

    # 다시 UTC 기준으로 환산
    noon_utc = local_noon - timedelta(hours=offset_hours)
    return int(noon_utc.timestamp())



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


def get_timezone(city_lat, city_lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=city_lat, lng=city_lon)
    if not tz_name:
        raise ValueError("해당 좌표에 대한 타임존을 찾을 수 없습니다.")

    return pytz.timezone(tz_name)

def get_current_utc_timestamp():
    return int(datetime.now(timezone.utc).timestamp())

def get_future_utc_timestamp(offset, mode: str):
    if(mode == "days"):
        future = datetime.now(timezone.utc) + timedelta(days=offset)
    elif(mode == "hours"):
        future = datetime.now(timezone.utc) + timedelta(hours=offset)
    return int(future.timestamp())

def get_future_utc_timestamp_from(timestamp, offset, mode: str = "hours"):
    dt = datetime.utcfromtimestamp(timestamp)
    if(mode == "hours"):
        future = dt + relativedelta(hours=offset)
    if(mode == "days"):
        future = dt + relativedelta(days=offset)
    return int(future.timestamp())

def one_year_ago_timestamp(timestamp: int) -> int:
    dt = datetime.utcfromtimestamp(timestamp)
    one_year_ago = dt - relativedelta(years=1)
    return int(one_year_ago.timestamp())

def one_year_after_timestamp(timestamp: int) -> int:
    dt = datetime.utcfromtimestamp(timestamp)
    one_year_after = dt + relativedelta(years=1)
    return int(one_year_after.timestamp())

def one_year_ago_timestamp_tz(timestamp: int, tz=None) -> int:
    """지정된 시간대 기준으로 정확히 1년 전 타임스탬프 반환"""
    if tz is None:
        tz = timezone.utc
    dt = datetime.fromtimestamp(timestamp, tz=tz)
    one_year_ago = dt - relativedelta(years=1)
    return int(one_year_ago.timestamp())

def one_year_after_timestamp_tz(timestamp: int, tz=None) -> int:
    """지정된 시간대 기준으로 정확히 1년 후 타임스탬프 반환"""
    if tz is None:
        tz = timezone.utc
    dt = datetime.fromtimestamp(timestamp, tz=tz)
    one_year_after = dt + relativedelta(years=1)
    return int(one_year_after.timestamp())



# 1, 2, 3, 4, 5를 1, 2, 3과 4, 5로 분할할
def split_sorted_list_bisect(lst, pivot):
    """정렬된 리스트를 기준값으로 분할 (bisect 사용)"""
    # bisect_right: pivot보다 큰 첫 번째 위치를 찾음
    # 기준값이 왼쪽에 포함
    idx = bisect.bisect_right(lst, pivot)
    return lst[:idx], lst[idx:]


def get_first_last_with_length(lst):
    """길이를 체크한 후 가져오기"""
    if len(lst) == 0:
        return None, None
    elif len(lst) == 1:
        return lst[0], lst[0]  # 원소가 하나면 첫 번째와 마지막이 같음
    else:
        return lst[0], lst[-1]