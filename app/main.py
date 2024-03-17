from fastapi import FastAPI

from app.router import setup_routes

app = FastAPI(
    title='Complex menu'
)

setup_routes(app=app)
