from fastapi import APIRouter, Depends
from sqlalchemy import select, asc, and_

from database import get_db
from models import Settle
from libs import JWTBearer

router = APIRouter()

'''
정산 대기열 리스트
'''
@router.get('/settles', dependencies=[Depends(JWTBearer())])
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
@router.post('/settles/{settle_id}', dependencies=[Depends(JWTBearer())])
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
