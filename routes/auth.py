from fastapi import APIRouter, Depends
from sqlalchemy import select

from database import get_db
from models import User
from dtos import *
from libs import encode_password, TokenProvider

router = APIRouter()

tokenProvider = TokenProvider()

@router.post("/login")
async def login(loginDto: LoginDto, session = Depends(get_db)):
    sql = select(User).where(User.email == loginDto.email)
    # session.flush()
    result: User = session.execute(sql).first()[0]
    token = tokenProvider.create_token(result)
    
    return token

@router.post("/register")
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
