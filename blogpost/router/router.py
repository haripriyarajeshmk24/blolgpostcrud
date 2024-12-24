from blogpost import schemas
import logging
from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from blogpost.db.database import get_db
from blogpost.db import models

app = APIRouter()

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    try:
        users = (
            db.query(models.User).all()
        )
        return {"status": "success", "response": users}
    except Exception as e:
        logging.error("Exception occurred. Cannot list the questions", exc_info=True)


@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == user.email).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"status": "success", "response": db_user}
    except:
        db.rollback()
        logging.error("Questions are updated", exc_info=True)
        return {"status": "failed", "response": "User cannot be updated"}