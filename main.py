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
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))  # Railway가 할당한 포트
    uvicorn.run("main:app", host="0.0.0.0", port=port)
