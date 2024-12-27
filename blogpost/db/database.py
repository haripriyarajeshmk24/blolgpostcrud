from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer

SQLALCHEMY_DATABASE_URL = 'postgresql://odoo17:odoo17@localhost/fastapi'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()