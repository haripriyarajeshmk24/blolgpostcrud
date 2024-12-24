from fastapi import FastAPI
from blogpost.router import router

app = FastAPI()

app.include_router(router.app)