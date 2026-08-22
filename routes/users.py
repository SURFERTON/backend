from fastapi import APIRouter, Depends
from sqlalchemy import select, asc

from database import get_db
from models import Post, Settle
from dtos import *
from libs import JWTBearer

router = APIRouter()

@router.get("/user", dependencies=[Depends(JWTBearer())])
async def getUser(payload: Payload = Depends(JWTBearer())):
    return payload

'''
내 요청 리스트 조회
'''
@router.get('/user/post', dependencies=[Depends(JWTBearer())])
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
정산 합계 보기
'''
@router.get('/user/settle', dependencies=[Depends(JWTBearer())])
async def getSettleSummation(payload:dict = Depends(JWTBearer()), session = Depends(get_db)):
    sql = select(Settle).where(Settle.user_id == payload['id'])
    result = session.execute(sql).all()
    ret = 0
    for i in result:
        ret += i[0].pay_amount
    
    return ret
