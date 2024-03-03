
from fastapi import FastAPI
from app.view.view import router

def setup_routes(app: FastAPI) -> None:
    app.include_router(router, prefix="", tags=["Menus"])