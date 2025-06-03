from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:3000"] (React 프론트 주소)
    allow_credentials=True,
    allow_methods=["*"],  # 여기에 "OPTIONS" 포함됨
    allow_headers=["*"],
)
