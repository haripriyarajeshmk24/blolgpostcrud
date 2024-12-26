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


class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    user_id: int
    post: list[Comment] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    username: str
    is_active: bool
    post: list[Post] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None