from pydantic import BaseModel
from datetime import datetime

class LoginDto(BaseModel):
    email: str
    password: str

class RegisterDto(BaseModel):
    email: str
    password: str
    name: str
    role: str
    
class PostDto(BaseModel):
    destination: str
    departure: str
    content: str
    end_time: datetime
    pay_amount: int
    tip: int

class RequestResumeScript(BaseModel):
    content: str

class Payload(BaseModel):
    id: int
    name: str
    email: str
    exp: str