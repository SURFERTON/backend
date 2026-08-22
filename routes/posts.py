from fastapi import APIRouter, Depends
from sqlalchemy import select, asc
from datetime import datetime

from database import get_db
from models import Post
from dtos import *
from libs import JWTBearer, sqlalchemy_obj_to_dict

router = APIRouter()

'''
Post CRUD
'''

'''
모든 요청 리스트 조회
'''
@router.get('/post')
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
요청 디테일 확인
'''
@router.get('/post/{post_id}')
async def getPostOne(post_id: int, session = Depends(get_db)):
    sql = select(Post).where(Post.id == post_id)
    result: Post|None = session.execute(sql).first()
    if result == None: return {"data": False}
    result = result[0]
    
    return {"data": result}

'''
요청 등록
'''
@router.post('/post', dependencies=[Depends(JWTBearer())])
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
@router.delete('/post/{post_id}', dependencies=[Depends(JWTBearer())])
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
해당 요청 상태
[배달 대기중, 배달중, 배달 완료, 배달 완료 확인 = 배달 종료 = 정산대기열]
[waiting, delivering, complete, finished]
'''
@router.get('/post-status/{post_id}', dependencies=[Depends(JWTBearer())])
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
