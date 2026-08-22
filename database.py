from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

required_db_variables = (
    "DB_USERNAME",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
)
missing_variables = [key for key in required_db_variables if not os.getenv(key)]

if missing_variables:
    raise RuntimeError(
        ".env에 다음 DB 설정이 필요합니다: " + ", ".join(missing_variables)
    )

DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

class engineconn:
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle=500)
        pass
    
    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
    
    def connection(self):
        conn = self.engine.connect()
        return conn

engine = engineconn()

def get_db():
    session = engine.sessionmaker()  # DB 연결 생성
    try:
        yield session                # 라우터 함수에 전달
    finally:
        session.close()              # 요청 종료 후 연결 종료
