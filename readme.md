# 애플리케이션 설치 및 실행 가이드

## 1. 저장소 클론

먼저 애플리케이션 저장소를 클론합니다

```bash
git clone https://github.com/Mobile-Programming-Team1/weather-api-backend.git
```

## 2. 프로젝트 디렉토리 이동

프로젝트 디렉토리로 이동합니다. (docker file들이 있고, app 디렉토리가 하위 디렉토리로 있는 디렉토리입니다)

## 3-1. Docker 설치된 경우 (필요한 경우)

Docker가 설치되어 있는 환경이라면 아래 명령어를 실행합니다.

```bash
docker compose up -d --build
```

## 3-2. 애플리케이션 실행

Docker가 설치되어 있지 않은 환경이라면 다음과 같이 의존성을 다운로드 한 뒤, 실행합니다.

```bash
pip install -r requirements.txt

uvicorn app.main:app --reload
```

## 4. Swagger UI 확인

다음 경로에서 Swagger가 제대로 나오는지 확인합니다.  
[http:127.0.0.1:8000/docs](http:127.0.0.1:8000/docs)
