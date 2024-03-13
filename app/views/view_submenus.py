from typing import List
from fastapi import APIRouter, Depends,  HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession
from app.redis.cache_submenu import SubMenuService
from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse


router = APIRouter()


################################
#      Endpoints for submenus  #
################################

@router.get("/api/v1/menus/{id}/submenus", response_model=List[SubMenuResponse])
async def get_submenus(id: int, db: AsyncSession = Depends(get_db)):
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.get_list_submenus(id_menu=id)
    return response


@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}", response_model=SubMenuResponse
)
async def get_submenu(
    id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)
):
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.get_one_submenu_by_id(id_menu=id_menu, id_submenu=id_submenu)
    return response


@router.patch(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}", response_model=SubMenuResponse
)
async def patch_submenu(
    id_menu: int,
    id_submenu: int,
    data: CreateSubMenuRequest,
    db: AsyncSession = Depends(get_db),
):
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.update_submenu(data=data, id_menu=id_menu, id_submenu=id_submenu)
    return response


@router.post(
    "/api/v1/menus/{id_menu}/submenus", response_model=SubMenuResponse, status_code=201
)
async def create_submenu(
    data: CreateSubMenuRequest, id_menu: int, db: AsyncSession = Depends(get_db)
) -> SubMenuResponse:
    submenu_service = SubMenuService(db=db)
    return await submenu_service.create_submenu(data=data, id_menu=id_menu)


@router.delete("/api/v1/menus/{id_menu}/submenus/{id_submenu}")
async def delete_submenu(
    id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)
):
    submenu_service = SubMenuService(db=db)
    await submenu_service.delete_submenu(id_menu=id_menu, id_submenu=id_submenu)