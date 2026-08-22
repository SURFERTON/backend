from fastapi import APIRouter, Depends
from sqlalchemy import select, asc, and_

from database import get_db
from models import Post, Settle
from libs import JWTBearer, sqlalchemy_obj_to_dict

router = APIRouter()

'''
Author 요청 완료
'''
@router.post('/auhtor-ok/{post_id}', dependencies=[Depends(JWTBearer())])
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
@router.get('/took', dependencies=[Depends(JWTBearer())])
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
@router.post('/took/{post_id}', dependencies=[Depends(JWTBearer())])
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
@router.post('/tooker-ok/{post_id}', dependencies=[Depends(JWTBearer())])
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
