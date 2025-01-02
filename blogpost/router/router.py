import schemas
import logging
from sqlalchemy.orm import joinedload
from db.database import get_db
from db import models
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token
from schemas import UserCreate, User
from jose import jwt
from jose.exceptions import JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from utils import create_access_token, JWTSECRET, JWTALGORITHM
from schemas import TokenData

from utils import get_password_hash, verify_password, JWTBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


app = APIRouter()


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWTSECRET, algorithms=[JWTALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/current_user", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


class PermissionChecker:

    def __init__(self, required_permissions: list[str]) -> None:
        self.required_permissions = required_permissions

    def __call__(self, user: User = Depends(get_current_user)) -> bool:
        for r_perm in self.required_permissions:
            if r_perm not in user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Permissions'
                )
        return True


@app.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        if current_user.role == "admin":
            users = db.query(models.User).options(joinedload(models.User.post)).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="UnAuthorized, Only admin can access user list"
            )
        return {"status": "success", "response": users}
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while loading the users: {str(e)}"
        )

@app.get("/posts",  dependencies=[Depends(JWTBearer())])
def get_all_posts(db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    try:
        print(current_user.role)
        if current_user.role == "user":
            posts = (
                db.query(models.Post).options(joinedload(models.Post.comments))
                .filter(models.Post.user_id == current_user.id) .all()
            )
        else:
            posts = (
                db.query(models.Post).options(joinedload(models.Post.comments)).all()
            )
        return {"status": "success", "response": posts}
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while loading the posts: {str(e)}"
        )

# @app.post("/users/{user_id}/posts", status_code=201)
# def create_post_for_user(user_id: int,post: schemas.PostCreate, db: Session = Depends(get_db)):
#     try:
#         db_user = db.query(models.User).filter(models.User.id == user_id).first()
#         if not db_user:
#             raise HTTPException(status_code=400, detail="User doesn't exist with given ID!")
#         db_item = models.Post(user_id=user_id, name=post.name, description=post.description)
#         db.add(db_item)
#         db.commit()
#         db.refresh(db_item)
#         return {"status": "success", "response": db_item}
#     except Exception as e:
#         db.rollback()
#         logging.error(f"Error occurred: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred while creating the post: {str(e)}"
#         )

@app.post("/users/{user_id}/posts", status_code=201, dependencies=[Depends(JWTBearer())])
def create_post_for_user(user_id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=400,
                detail="User doesn't exist with given ID!"
            )

        db_item = models.Post(
            user_id=user_id,
            name=post.name,
            description=post.description
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return {"status": "success", "response": db_item}
    except Exception as e:
        db.rollback()
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the post: {str(e)}"
        )


@app.get("/comments")
def get_all_comments(db: Session = Depends(get_db)):
    try:
        comments = (
            db.query(models.Comment).all()
        )
        return {"status": "success", "response": comments}
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise  HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while loading the comments: {str(e)}"
        )

@app.post("/posts/{post_id}/comment", status_code=201)
def create_comment_for_post(post_id: int,comment: schemas.CommentBase, db: Session = Depends(get_db)):
    try:
        db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not db_post:
            raise HTTPException(status_code=400, detail="Post doesn't exist with given ID!")
        db_comment = models.Comment(post_id=post_id, name=comment.name, description=comment.description)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return {"status": "success", "response": db_comment}
    except Exception as e:
        db.rollback()
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the comment: {str(e)}"
        )