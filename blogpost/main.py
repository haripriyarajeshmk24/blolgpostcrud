from fastapi import FastAPI
from router import router
from db.database import engine
from db.models import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(router.app)