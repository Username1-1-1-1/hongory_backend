from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(api_router)
origins = [
    "https://hongory-frontend-final.vercel.app",  # Vercel 배포 주소
    "http://localhost:3000"  # 로컬 개발 환경
]
@app.get("/")
def root():
    return {"message": "FastAPI is working!"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 또는 ["http://localhost:3000"] (React 프론트 주소)
    allow_credentials=True,
    allow_methods=["*"],  # 여기에 "OPTIONS" 포함됨
    allow_headers=["*"],
)
