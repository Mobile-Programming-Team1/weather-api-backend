from fastapi import APIRouter
from ..model import CitiesResponse
from ..loader import CITIES_DATA

router = APIRouter()

@router.get("/cities", response_model=CitiesResponse)
async def get_cities():
    
    # 응답 형식으로 변환
    response = {"cities": CITIES_DATA}
    
    return response