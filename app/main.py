from fastapi import FastAPI
from app import router_weather, router_city
app = FastAPI(title="OpenWeather API 프록시", description="OpenWeather API 데이터를 전처리하여 제공하는 API")


app.include_router(router_weather, tags=["weather"])
app.include_router(router_city, tags=["city"])