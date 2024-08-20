from fastapi import FastAPI, Depends, UploadFile, HTTPException
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import select, asc, and_, or_
import os
import uvicorn
from datetime import datetime

# custom modules
from database import engineconn
from models import Base, User, Post, Settle
from dtos import *
from libs import encode_password, JWTBearer, TokenProvider, JWTBearerOrNone, sqlalchemy_obj_to_dict
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
engine = engineconn()

def get_db():
    session = engine.sessionmaker()
    try:
        yield session
    finally:
        session.close()

# 모든 테이블 초기화
Base.metadata.drop_all(bind=engine.engine)
Base.metadata.create_all(bind=engine.engine) 

# TODO 회원가입, 로그인, 토큰, 이미지 업로드, 이미지 다운로드, 게시판 crud (연관관계 테스트)


tokenProvider = TokenProvider()

@app.get('/')
async def root():
    return "Hello, '강'!"

@app.post("/login")
async def login(loginDto: LoginDto, session = Depends(get_db)):
    sql = select(User).where(User.email == loginDto.email)
    # session.flush()
    result: User = session.execute(sql).first()[0]
    token = tokenProvider.create_token(result)
    
    return token

@app.post("/register")
async def register(dto: RegisterDto, session = Depends(get_db)):
    user = User()
    user.name = dto.name
    user.email = dto.email
    user.password = encode_password(dto.password)
    user.role = dto.role.lower()
    user.verified = True # 인증 완료 자동
    session.add(user)
    session.commit()
    token = tokenProvider.create_token(user)
    
    return token

@app.get("/user", dependencies=[Depends(JWTBearer())])
async def getUser(payload: Payload = Depends(JWTBearer())):
    return payload

@app.post("/image")
async def upload_image(file: UploadFile):
    DIR = './image'
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    content = await file.read()
    extension_index = file.filename.rindex('.')
    # filename_extension = file.filename[extension_index+1:]
    filename = file.filename[:extension_index]

    image_extensions = ('.jpg', '.jprg', '.png', '.gif', '.bmp', '.tiff', '.svg')
    if not file.filename.lower().endswith(image_extensions):
        return { "detail": "This file is not image file." }
    
    with open(os.path.join(DIR, filename), "wb") as fp:
        fp.write(content)
    return {"filename": filename}

'''
Post CRUD
'''

'''
모든 요청 리스트 조회
'''
@app.get('/post')
async def getPosts(page: int = 1, size: int = 10, session = Depends(get_db)):
    # 페이지네이션을 위한 기본 값 설정
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    # 오프셋 계산 (몇 번째 항목부터 가져올지)
    offset = (page - 1) * size

    # now가 endtime보다 느리면 필터링해서 제외함.
    now_time = datetime.now()
    posts = session.query(Post)\
        .filter(Post.end_time > now_time)\
        .order_by(asc(Post.created_at)).offset(offset).limit(size).all()
    
    return posts

'''
내 요청 리스트 조회
'''
@app.get('/user/post', dependencies=[Depends(JWTBearer())])
async def getUserPosts(page: int = 1, size: int = 10, payload:dict = Depends(JWTBearer()), session = Depends(get_db)):
    # 페이지네이션을 위한 기본 값 설정
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    # 오프셋 계산 (몇 번째 항목부터 가져올지)
    offset = (page - 1) * size
    author_id = payload['id']
    # SQLAlchemy 쿼리로 페이지네이션 적, session = Depends(get_db)용

    posts = session.query(Post)\
        .where(Post.author_id == author_id).order_by(asc(Post.created_at)).offset(offset).limit(size).all()
    
    return posts

'''
요청 디테일 확인
'''
@app.get('/post/{post_id}')
async def getPostOne(post_id: int, session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None: return {"data": False}
    result = result[0]
    
    return {"data": result}

'''
요청 등록
'''
@app.post('/post', dependencies=[Depends(JWTBearer())])
async def createPost(dto: PostDto, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    post = Post()
    post.author_id = payload['id']
    post.content = dto.content
    post.end_time = dto.end_time
    post.destination = dto.destination
    post.departure = dto.departure
    post.pay_amount = dto.pay_amount
    post.tip = dto.tip

    session.add(post)
    session.commit()
    return sqlalchemy_obj_to_dict(post)


'''
요청 삭제
'''
@app.delete('/post/{post_id}', dependencies=[Depends(JWTBearer())])
async def deletePost(post_id: int, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None:
        return {"data": False}
    result = result[0]
    
    if result.author_id != payload['id']:
        return {"detail": "You don't have permission no delete this post." }
    session.delete(result)
    session.commit()
    return { "data": True }


'''
Author 요청 완료
'''
@app.post('/auhtor-ok/{post_id}', dependencies=[Depends(JWTBearer())])
async def authorOk(post_id: int, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None:
        return {"data": False}
    result = result[0]
    print(result.tooker_ok)

    if result.tooker_ok == False:
        return {"data": False, "detail": "Tooker didn't delivery yet."}

    if result.author_ok:
        return {"data": False, "detail": "Already done."}

    if result.author_id != payload['id']:
        return {"detail": "You don't have permission no author-ok this post."}
    result.author_ok = True
    session.add(result)
    session.commit()
    # 배달 종료, 정산 대기열 추가
    settle = Settle()
    settle.pay_amount = result.tip
    settle.user_id = result.tooker_id
    session.add(settle)
    session.commit()
    session.refresh(settle)
    
    return {"data": True}

'''
Tooker 심부름 리스트
'''
@app.get('/took', dependencies=[Depends(JWTBearer())])
async def getTooks(page: int = 1, size: int = 10, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    offset = (page - 1) * size

    settles = session.query(Post)\
        .where(
            and_(
                Post.tooker_ok == False,
                Post.tooker_id == payload['id']
            )
        )\
        .order_by(asc(Post.id)).offset(offset).limit(size).all()
    
    return settles

'''
Tooker 심부름 수락
'''
@app.post('/took/{post_id}', dependencies=[Depends(JWTBearer())])
async def tookerStart(post_id: int, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post | None = session.execute(sql).first()
    if result == None:
        return {'data': False}
    result = result[0]
    # if result.tooker_id == payload['id']:
    #     return {'data': False, 'detail': 'Poster cannot same with tooker'}
    if result.tooker_id != None:
        return {'data': False, 'detail': 'Already started.'}
    result.tooker_id = payload['id']
    session.add(result)
    session.commit()
    session.refresh(result)
    
    return sqlalchemy_obj_to_dict(result)

'''
Tooker 심부름 완료
'''
@app.post('/tooker-ok/{post_id}', dependencies=[Depends(JWTBearer())])
async def tookerOk(post_id: int, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None:
        return {"data": False}
    result = result[0]

    if result.tooker_id != payload['id']:
        return {"data":False, "detail": "You don't have permission no tooker-ok this post."}
    result.tooker_ok = True
    session.add(result)
    session.commit()
    
    return {"data": True}


'''
해당 요청 상태
[배달 대기중, 배달중, 배달 완료, 배달 완료 확인 = 배달 종료 = 정산대기열]
[waiting, delivering, complete, finished]
'''
@app.get('/post-status/{post_id}', dependencies=[Depends(JWTBearer())])
async def postStatus(post_id: int, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None:
        return {"data": False}
    result = result[0]
    user_id = payload['id']
    if result.author_id != user_id and result.tooker_id != user_id:
        return {"data": False, "detail": "You can't look up this post."}
    # waiting 
    if result.tooker_id == None:
        return {"data": "waiting"}
    if result.tooker_ok and result.author_ok:
        return {"data": "finished"}
    if result.tooker_ok:
        return {"data": "complete"}
    
    return {"data": "delivering"}


'''
정산 대기열 리스트
'''
@app.get('/settles', dependencies=[Depends(JWTBearer())])
async def getSettles(page: int = 1, size: int = 10, payload: dict = Depends(JWTBearer()), session = Depends(get_db)):
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    offset = (page - 1) * size

    settles = session.query(Settle)\
        .where(
            and_(
                Settle.is_settled == False,
                Settle.user_id == payload['id']
            )
        )\
        .order_by(asc(Settle.id)).offset(offset).limit(size).all()
    
    return settles

'''
정산하기
'''
@app.post('/settles/{settle_id}', dependencies=[Depends(JWTBearer())])
async def doSettle(settle_id: int, payload:dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Settle).where(Settle.id == settle_id)
    result: Settle|None = session.execute(sql).first()
    if result == None:
        return {'data': False}
    result = result[0]
    if result.is_settled:
        return {'data': False, 'detail': 'Already done.'}
    result.is_settled = True
    session.add(result)
    session.commit()
    
    return {'data': result.pay_amount}

'''
정산 합계 보기
'''
@app.get('/user/settle', dependencies=[Depends(JWTBearer())])
async def getSettleSummation(payload:dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Settle).where(Settle.user_id == payload['id'])
    result = session.execute(sql).all()
    ret = 0
    for i in result:
        ret += i[0].pay_amount
    
    return ret


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3001, reload=True)
