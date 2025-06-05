# weather_checker.py
import os
import firebase_admin
from .environ import OPENWEATHER_API_KEY as API_KEY
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
        "./credentials.json"
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
        "appid": API_KEY
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
    docs = firebase_db.collection("plans").stream()
    docs_list = list(docs)
    print(f"🔄 총 처리할 문서 수: {len(docs_list)}")

    # ← 여기서부터 수동으로 사용할 FCM 토큰을 지정하세요.
    token = "d9HFDFKWRcWmgz8x7KrxrJ:APA91bEJ_lp6_5Eec95xx9kQGm1AredF20vXScSG8StvFbs4bWi12OlDkKFiZB3Fltd42oPFUASuPMXND5DNunGcUQjzO6qrkmNs6zj5Rnq5SRP4__nQk_s"

    for doc in docs_list:
        data = doc.to_dict()
        print(f"📦 plans 문서 내용: {data}")

        destination = data.get("destination")
        weather_list = data.get("weather", [])
        if not destination or not weather_list:
            continue

        expected_list = []
        for item in weather_list:
            date_str = item.get("date")
            cond = item.get("condition")
            if date_str and cond:
                expected_list.append((date_str, cond.upper()))

        for date_str, expected_cond in expected_list:
            time.sleep(1.1)  # OpenWeatherMap API 호출 제한을 피하기 위해
            city_input = destination.strip().title()
            actual_cond = get_real_weather(city_input, date_str)
            if expected_cond.lower() != actual_cond.lower():
                print(f"❗차이 발생: {destination} | {date_str} | 예상: {expected_cond}, 실제: {actual_cond}")
                title = f"{date_str} 날씨 변경"
                body = f"{destination}의 날씨가 예상({expected_cond})과 달라요! 실제: {actual_cond}"
                send_fcm_v1(token, title, body)
            else:
                print(f"✅ 일치: {destination} | {date_str} | {expected_cond}")

    print("✅ 날씨 비교 완료: ", datetime.now().isoformat())


