# weather_checker.py
import os
import firebase_admin
#from .environ import OPENWEATHER_API_KEY as API_KEY
#from environ import OPENWEATHER_API_KEY as API_KEY

from firebase_admin import credentials, messaging, firestore
import requests
from datetime import datetime, timedelta
import time
import schedule


firebase_db = None


def schedule_weather_checker():
    global firebase_db

    # 1) Firebase Admin SDK 초기화
    firebase_credential = credentials.Certificate(
        "./app/credentials.json" #./credentials.json
    )
    firebase_admin.initialize_app(firebase_credential)
    firebase_db = firestore.client()
    schedule.every(1).minutes.do(check_and_notify)

def get_real_weather(city: str, date_str: str) -> str:
    base_url = "http://localhost:8000/weather/"
    date_nohyphen = date_str.replace("-", "")
    params = {
        "city": city,
        "start_date": date_nohyphen,
        "end_date": date_nohyphen,
   #     "appid": afad7c87ebd1b14f5287168defd8d921
    }

    print(f"→ [DEBUG] 호출 URL: {base_url} params={params}")
    try:
        resp = requests.post(base_url, params=params)
        print("→ [DEBUG] 실제 Request URL :", resp.request.url)
        print("→ [DEBUG] 실제 Request headers:", resp.request.headers)
        print(f"← [DEBUG] Response status: {resp.status_code}")
        print("← [DEBUG] Response headers:", resp.headers)
        print("← [DEBUG] Response body:", resp.text)

        if resp.status_code == 200:
            data = resp.json()
            forecast_list = data.get("forecast", [])
            if forecast_list and isinstance(forecast_list, list):
                weather_str = forecast_list[0].get("weather")
                if weather_str:
                    return weather_str.upper()
        return "UNKNOWN"
    except Exception as ex:
        print(f"⚠️ [ERROR] get_real_weather 예외: 도시={city}, 날짜={date_str}, 예외={ex}")
        return "UNKNOWN"

def send_fcm_v1(token: str, title: str, body: str) -> None:
    message = messaging.Message(
        data={
            "title": title,
            "body": body
        },
        token=token
    )

    try:
        print(f">>> send_fcm_v1() 호출: token={token}, title={title}, body={body}")
        response = messaging.send(message)
        print(f"📬 v1 데이터 메시지 전송 완료: {response}")
    except Exception as e:
        print(f"⚠️ FCM 전송 실패: {e}")

def check_and_notify():
    print("🔍 날씨 비교 시작: ", datetime.now().isoformat())

    users_ref = firebase_db.collection("users").stream()

    for user_doc in users_ref:
        user_id = user_doc.id
        user_data = user_doc.to_dict()
        token = user_data.get("token")

        if not token:
            continue

        print(f"🧾 사용자 문서: {user_id}")
        print(f"🔑 해당 사용자 토큰: {token}")

        trips_ref = firebase_db.collection("users").document(user_id).collection("trips").stream()

        for trip_doc in trips_ref:
            trip_data = trip_doc.to_dict()
            print(f"📦 trip 문서 내용: {trip_data}")

            destination = trip_data.get("destination")
            weather_list = trip_data.get("weather", [])

            for item in weather_list:
                date_str = item.get("date")
                expected_cond = item.get("condition", "").upper()

                if not destination or not date_str or not expected_cond:
                    continue

                time.sleep(1.1)  # API 제한 고려
                actual_cond = get_real_weather(destination, date_str)

                if expected_cond.lower() != actual_cond.lower():
                    print(f"❗차이 발생: {destination} | {date_str} | 예상: {expected_cond}, 실제: {actual_cond}")
                    title = f"[날씨 변화] {destination} - {date_str}"
                    body = f"예상: {expected_cond}, 실제: {actual_cond}"
                    send_fcm_v1(token, title, body)
                else:
                    print(f"✅ 일치: {destination} | {date_str} | {expected_cond}")

    print("✅ 날씨 비교 완료: ", datetime.now().isoformat())
if __name__ == "__main__":
    schedule_weather_checker()
    check_and_notify()
    while True:
        schedule.run_pending()
        time.sleep(1)