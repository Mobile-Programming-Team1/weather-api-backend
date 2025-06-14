from fastapi import FastAPI
from app import router_weather, router_city, router_air, router_token, router_recomm
from app import scheduled_task
import logging
import threading
from .weather_checker import schedule_weather_checker

logging.basicConfig(
    filename='app.log',  # 로그 파일명
    level=logging.INFO,  # 로그 레벨 설정
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',  # 파일명, 라인번호, 함수명 포함
    datefmt='%Y-%m-%d %H:%M:%S',  # 날짜 형식
    encoding='utf-8'  # 한글 지원을 위한 인코딩
)


app = FastAPI(title="OpenWeather API 프록시", description="OpenWeather API 데이터를 전처리하여 제공하는 API")


app.include_router(router_weather, tags=["weather"])
app.include_router(router_city, tags=["city"])
app.include_router(router_air, tags=["air"])
app.include_router(router_token, tags=["token"])
app.include_router(router_recomm, tags=["recommend"])





@app.on_event("startup")
async def startup_event():
    # 백그라운드 스레드에서 스케줄러 실행
    scheduler_thread = threading.Thread(target=schedule_weather_checker, daemon=True)
    scheduler_thread.start()