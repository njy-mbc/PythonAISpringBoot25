from fastapi import FastAPI
from pydantic import BaseModel
# 데이터 유효성 검사와 설정 관리에 사용되는 라이브러리(모델링이 쉽고 강력함)
from starlette.middleware.base import BaseHTTPMiddleware
# 요청과 응답 사이에서 특정 작업 수행
# 미들웨어는 모든 요청에 대해 실행되며, 요청을 처리하기 전에 응답을 반환하기 전, 특정 작업을 수행할 수 있음
# 예를 들어 로깅, 인증, cors처리, 압축 등...
import logging # 로깅 처리용 매서드

app = FastAPI( # 앱의 시그니쳐와 환경설정을 담당
    title = "MBC AI study",
    description="MBC AI study",
    version="0.0.1",
    docs_url=None,  # 보안상 접근 불가설정
    redoc_url=None, # 상동
) # java -> new FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):    # 로그를 콘솔에 출력하는 용도
    logging.basicConfig(level=logging.INFO)      # 로그 출력 추가
    async def dispatch(self, request, call_next):
        logging.info(f"Req:{request.method}, {request.url}")
        response = await call_next(request)
        logging.info(f"Status Code:{response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)   # 모든 요청에 대해 로그를 남기는 미들웨어 클래스를 사용함

class Item(BaseModel): # Item 객체 검증용(BaseModel, 객체 연결 -> 상속)
    name: str                   # 상품명 : 문자열()
    description: str = None     # 상품설명 : 문자열(null)
    price: float                # 가격 : 실수형
    tax: float = None           # 세금 : 실수형(null)

@app.get("/")   # 웹 브라우저에 http://localhost:8000/ -> get 요청시 처리
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")   # http://localhost:8001/items/1 -> get 요청시
async def reate_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/") # post 매서드용 요청 (create)
async def create_item(item: Item):
    # BaseModel은 데이터 모델링을 쉡게 도와주고 유효성 검사도 수행
    # 잘못된 데이터가 들어오면 422 오류코드를 반환
    return item

# postman은 프론트가 없는 백엔드 테스트용 프로그램으로 활용
# 서버실행은 uvicorn main:app --reload --port 8001
# uvicorn : 파이썬 백엔드 가동 서버 main.py에 있는 app 매서드를 사용
# --reload : 서버 갱신
# --port 8001 : 8001 포트 사용