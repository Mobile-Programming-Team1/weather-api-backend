from fastapi import APIRouter
from ..model import StatusResponse

router = APIRouter()

@router.get("/token", response_model=StatusResponse)
async def save_token(token: str):
    # 사용자 정보 리스트 DB에 토큰 저장

    response = {"status": "ok"}
    return response