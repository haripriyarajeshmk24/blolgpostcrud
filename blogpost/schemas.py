from pydantic import BaseModel

class CommentBase(BaseModel):
    name: str
    description: str| None = None


class Comment(CommentBase):
    id: int
    post_id: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    name: str
    description: str| None = None


class Post(PostBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    username: str
    is_active: bool
    post: list[Post] = []

    class Config:
        orm_mode = True
