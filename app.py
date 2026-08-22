from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# custom modules
from database import engine
from models import Base
from routes import auth, users, posts, deliveries, settlements, images
# from aimodule import create_prediction_prompt

app = FastAPI()

# cors config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모든 테이블 초기화
Base.metadata.drop_all(bind=engine.engine)
Base.metadata.create_all(bind=engine.engine) 

# TODO 회원가입, 로그인, 토큰, 이미지 업로드, 이미지 다운로드, 게시판 crud (연관관계 테스트)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(deliveries.router)
app.include_router(settlements.router)
app.include_router(images.router)

@app.get('/')
async def root():
    return "Hello, '강!'"


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3001, reload=True)
