
from fastapi import FastAPI
from app.views.view_menus import router as router_menus
from app.views.view_submenus import router as router_submenus
from app.views.view_dishes import router as router_dishes

def setup_routes(app: FastAPI) -> None:
    app.include_router(router_menus, prefix="", tags=["Menus"])
    app.include_router(router_submenus, prefix="", tags=["SubMenus"])
    app.include_router(router_dishes, prefix="", tags=["Dishes"])