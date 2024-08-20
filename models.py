from sqlalchemy import Column, TEXT, INT, BIGINT, String, Text, ForeignKey, DateTime, Null, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import 
from datetime import datetime

Base = declarative_base()

class User(Base):
   __tablename__ = "user"

   id = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
   name = Column(TEXT, nullable=False)
   email = Column(String(255), nullable=False, unique=True)
   password = Column(TEXT, nullable=False)
   role = Column(TEXT, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
   verified = Column(INT, default=0)
   

   posts = relationship("Post", foreign_keys="[Post.author_id]", back_populates="author")
   tooks = relationship("Post", foreign_keys="[Post.tooker_id]", back_populates="tooker")
   settles = relationship("Settle", foreign_keys="[Settle.user_id]", back_populates="user")

class Post(Base):
   __tablename__ = "post"

   id = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
   content = Column(Text, nullable=False)
   author_id = Column(BIGINT, ForeignKey("user.id"), nullable=False)
   tooker_id = Column(BIGINT, ForeignKey("user.id"), nullable=True)
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
   end_time = Column(DateTime, nullable=False)
   destination = Column(Text, nullable=False)
   departure = Column(Text, nullable=False)
   author_ok = Column(Boolean, default=False, nullable=False)
   tooker_ok = Column(Boolean, default=False, nullable=False)
   pay_amount = Column(INT, default=0, nullable=False)
   tip = Column(INT, default=1000, nullable=False)
   # settle = Column(Boolean, default=False, nullable=False)

   author = relationship("User", foreign_keys=[author_id], back_populates="posts")
   tooker = relationship("User", foreign_keys=[tooker_id], back_populates="tooks")

class Settle(Base):
   __tablename__ = "settle"

   id = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
   user_id = Column(BIGINT, ForeignKey("user.id"), nullable=False)
   pay_amount = Column(INT, nullable=False)
   is_settled = Column(Boolean, default=False, nullable=False)

   user = relationship("User", foreign_keys=[user_id], back_populates="settles")