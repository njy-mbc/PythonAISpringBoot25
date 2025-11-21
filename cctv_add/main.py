# main.py

# 라이브러리 임포트
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import io
import base64
from PIL import Image
import numpy as np
from ultralytics import YOLO
import cv2
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# FastAPI 앱 생성
app = FastAPI()

# 로깅 설정
logging.basicConfig(level=logging.INFO)


# 미들웨어 정의
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logging.info(f'Req : {request.method} {request.url}')
        response = await call_next(request)
        logging.info(f'Status Code : {response.status_code}')
        return response


app.add_middleware(LoggingMiddleware)

# YOLOv8 모델 로드
model = YOLO('yolov8n.pt')


# 응답 모델 정의
class DetectionResult(BaseModel):
    message: str  # 클라이언트가 보낸 원본 메시지
    image: str  # Base64로 인코딩된 결과 이미지


# 객체 탐지 함수 (수정됨)
def detect_objects(image: Image):
    # PIL 이미지를 numpy 배열로 변환
    img = np.array(image)

    # PIL(RGB) -> OpenCV(BGR) 변환 (OpenCV 처리를 위해)
    # 만약 원본 색상이 이상하면 이 변환 과정을 확인해야 함
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    results = model(img)  # 객체 탐지 수행

    # 탐지된 결과를 이미지에 그리기
    for result in results:
        boxes = result.boxes  # Boxes 객체 가져오기

        for box in boxes:
            # 좌표 가져오기 (Tensor -> List -> int)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # 신뢰도 가져오기
            conf = float(box.conf[0])

            # 클래스 이름 가져오기
            cls = int(box.cls[0])
            label_name = model.names[cls]

            # 사각형 그리기 (오타 수정: retangle -> rectangle)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # 텍스트 쓰기
            caption = f'{label_name} {conf:.2f}'
            cv2.putText(img, caption, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # 결과 이미지를 다시 PIL Image 객체로 변환
    result_image = Image.fromarray(img)
    return result_image

@app.get("/")
async def index():
    return {"message": "Hello FastAPI!"}


@app.post("/detect", response_model=DetectionResult)
async def detect_service(message: str = Form(...), file: UploadFile = File(...)):
    # 업로드된 파일을 읽어서 PIL 이미지로 변환
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # 알파 채널(투명도) 제거 및 RGB로 변환
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # 객체 탐지 수행
    result_image = detect_objects(image)

    # 결과 이미지를 메모리 버퍼에 저장 (JPEG 포맷)
    buffered = io.BytesIO()
    # 오타 수정: JEPG -> JPEG
    result_image.save(buffered, format="JPEG")

    # Base64 인코딩
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 결과 반환 (message에는 입력받은 message를, image에는 인코딩된 이미지를 넣음)
    return DetectionResult(message=message, image=img_str)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)