import pandas as pd

CITIES_DATA = []

try:
    df = pd.read_csv("app/data/cities_list.CSV")
    # DataFrame을 딕셔너리 목록으로 변환
    for _, row in df.iterrows():
        city = {
            "name": row["name"],
            "country": row["country"],
            "lon": float(row["lon"]),
            "lat": float(row["lat"])
        }
        CITIES_DATA.append(city)
except Exception as e:
    print(f"CSV 파일 로드 중 오류 발생: {str(e)}")

    