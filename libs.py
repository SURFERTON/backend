import bcrypt
import jwt
import models
import datetime
from fastapi import status, Security, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

'''
libs 모듈에 사용하는 상수입니다.
'''
SECRET = 'rkdskaeosecret'
EXPIRED_SECONDS = 3000
ALGORITHM = 'HS256'

def encode_password(password: str):
    """
    비밀번호를 암호화합니다.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def validate_password(password: str, hashed_password: str):
    """
    비밀번호를 검증합니다.
    """
    return bcrypt.checkpw(password=password, hashed_password=hashed_password)


class JWTBearerOrNone(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        self.tokenProvider = TokenProvider()
        super(JWTBearerOrNone, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        except:
            return None
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authentication scheme.')
            if not credentials.credentials:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='There is no token.')
            token = credentials.credentials
            if self.tokenProvider.validate_token(token) == status.HTTP_401_UNAUTHORIZED:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token or expired token.')
            return self.tokenProvider.decode_token(token)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.')


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        self.tokenProvider = TokenProvider()
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authentication scheme.')
            if not credentials.credentials:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='There is no token.')
            token = credentials.credentials
            if self.tokenProvider.validate_token(token) == status.HTTP_401_UNAUTHORIZED:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token or expired token.')
            return self.tokenProvider.decode_token(token)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.')
        
class TokenProvider:
    """
    유저 payload를 담는 jwt 생성, 검증을 위한 클래스입니다.
    __new__() 와 __init__() 함수는 싱글톤 생성을 위해 override했습니다. 
    TokenProvider 객체는 Singleton 객체입니다.
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            cls._init = True

    def create_token(self, user: models.User):
        """
        유저 토큰을 생성합니다. payload는 'id', 'name', 'email'입니다. EXPRIED_SECONDS는 생성순간으로부터의 만료시간입니다.
        """
        encoded = jwt.encode({
            'exp': datetime.datetime.now() + datetime.timedelta(seconds=EXPIRED_SECONDS),
            'id': user.id,
            'name': user.name,
            'email': user.email
        }, SECRET, algorithm=ALGORITHM)
        return encoded

    def validate_token(self, token: str):
        """
        토큰을 검증합니다. 유요하지 않으면 Http status를 리턴합니다. 유효하면 True를 리턴합니다.
        """
        try:
            jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return status.HTTP_401_UNAUTHORIZED
        except jwt.InvalidTokenError:
            return status.HTTP_401_UNAUTHORIZED
        else:
            return True
        
    def decode_token(self, token: str):
        """
        토큰을 decode하여 payload를 반환합니다.
        """
        try:
            payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            return payload
        except:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

def sqlalchemy_obj_to_dict(obj):
    """
    SQLAlchemy 모델 객체를 JSON 직렬화가 가능한 dict로 변환합니다.
    """
    if isinstance(obj.__class__, DeclarativeMeta):
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                json.dumps(data)  # 이 필드가 JSON으로 직렬화 가능한지 확인
                fields[field] = data
            except TypeError:
                fields[field] = str(data)
        return fields
    return obj

# user = models.User()
# user.password = 'asd'
# user.email = 'mysql@email.com'
# user.name = 'myname'
# user.id = 1

# print(createToken(user))