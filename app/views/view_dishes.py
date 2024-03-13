from typing import List
from fastapi import APIRouter, Depends,  HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession
from app.redis.cache_dishes import DishesService
from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse


router = APIRouter()


################################
#      Endpoints for dishes    #
################################

@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes",
    response_model=List[DishesResponse],
)
async def get_dishes(id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)):
    dishes_service = DishesService(db=db)
    response = await dishes_service.get_list_dishes(id_menu=id_menu, id_submenu=id_submenu)
    return response


@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
    response_model=DishesResponse,
)
async def get_dish(
    id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)
):
    dishes_service = DishesService(db=db)
    response = await dishes_service.get_one_dish_by_id(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes)
    return response


@router.patch(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
    response_model=DishesResponse,
)
async def patch_dish(
    id_menu: int,
    id_submenu: int,
    id_dishes: int,
    data: CreateDishesRequest,
    db: AsyncSession = Depends(get_db),
):
    dishes_service = DishesService(db=db)
    response = await dishes_service.update_dish(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes, data=data)
    return response


@router.post(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes",
    response_model=DishesResponse,
    status_code=201,
)
async def create_dish(
    data: CreateDishesRequest,
    id_menu: int,
    id_submenu: int,
    db: AsyncSession = Depends(get_db),
) -> DishesResponse:
    submenu_service = DishesService(db=db)
    return await submenu_service.create_dish(data=data, id_menu=id_menu, id_submenu=id_submenu)


@router.delete(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
)
async def delete_dishes(
    id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)
):
    submenu_service = DishesService(db=db)
    await submenu_service.delete_dish(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes)