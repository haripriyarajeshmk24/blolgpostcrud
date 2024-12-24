from sqlalchemy.orm import relationship

from blogpost.db.database import Base
from sqlalchemy import (
    Integer,
    String,
    Column,
    Boolean,
    ForeignKey,
)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    user_status = Column(Boolean, nullable=False)

    post = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    comments = relationship("Comment", back_populates="owner")
    user = relationship("User", back_populates="post")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"))


    post = relationship("Post", back_populates="comments")