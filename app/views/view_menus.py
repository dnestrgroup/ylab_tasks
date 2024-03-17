from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from app.redis.cache_menu import MenuService
from app.repositories.rep_menu import RepositoriesMenus
from app.schemas.schemas import CreateMenuRequest, MenuResponse
from app.services.cache_invalidation import cache_invalidation

router = APIRouter()

################################
#      Endpoints for menus     #
################################


@router.get('/api/v1/all', summary='Сложная структура данных из всех меню подменю и блюд (Дз №4)')  # type: ignore
async def get_menus_all(db: AsyncSession = Depends(get_db)) -> list[dict[Any, list[dict[Any, list[dict[str, Any]]]]]]:
    menu_service = RepositoriesMenus(db=db)
    response = await menu_service.get_all()
    return response


@router.get('/api/v1/menus', response_model=list[MenuResponse], summary='Метод получения списка меню')  # type: ignore
async def get_menus(db: AsyncSession = Depends(get_db)) -> list[MenuResponse]:
    menu_service = MenuService(db=db)
    response = await menu_service.get_list()
    return response


@router.get('/api/v1/menus/{id}', response_model=MenuResponse, summary='Метод получения меню по id')  # type: ignore
async def get_menu(id: int, db: AsyncSession = Depends(get_db)) -> MenuResponse:
    query = select(MainMenu).filter(MainMenu.id == id)
    res = (await db.execute(query)).scalar_one_or_none()
    if res is not None:
        submenus_query = select(func.count(SubMenu.id)).where(SubMenu.main_menu_id == id)
        submenus_count = (await db.execute(submenus_query)).scalar()

        submenus = select(SubMenu.id).where(SubMenu.main_menu_id == id)
        submenus_results = await db.execute(submenus)
        submenu_ids = [result[0] for result in submenus_results]

        dishes_query = select(func.count(Dishes.id)).where(Dishes.sub_menu_id.in_(submenu_ids))
        dishes_count = (await db.execute(dishes_query)).scalar()

        return MenuResponse(
            id=str(res.id),
            title=res.title,
            description=res.description,
            submenus_count=submenus_count,
            dishes_count=dishes_count,
        )
    raise HTTPException(status_code=404, detail='menu not found')


@router.post('/api/v1/menus', response_model=MenuResponse, status_code=201, summary='Метод создания пункта меню')  # type: ignore
async def create_menu(data: CreateMenuRequest, db: AsyncSession = Depends(get_db)) -> MenuResponse:
    menu_service = MenuService(db=db)
    return await menu_service.create_menu(data=data)


@router.patch('/api/v1/menus/{id}', response_model=MenuResponse, summary='Метод обновления пункта меню')  # type: ignore
async def patch_menu(
    background_tasks: BackgroundTasks,
    id: int,
    data: CreateMenuRequest,
    db: AsyncSession = Depends(get_db),
) -> MenuResponse:
    query = (
        update(MainMenu)
        .where(MainMenu.id == id)
        .values(title=data.title, description=data.description)
        .returning(MainMenu.id, MainMenu.title, MainMenu.description)
    )
    res = (await db.execute(query)).fetchone()
    await db.commit()
    background_tasks.add_task(cache_invalidation, '/api/v1/menus/' + str(id))
    return MenuResponse(id=str(res[0]), title=res[1], description=res[2], submenus_count=None, dishes_count=None)


@router.delete('/api/v1/menus/{id}', summary='Метод удаления пункта меню')  # type: ignore
async def delete_menu(background_tasks: BackgroundTasks, id: int, db: AsyncSession = Depends(get_db)) -> None:
    menu_service = MenuService(db=db)
    background_tasks.add_task(cache_invalidation, '/api/v1/menus/' + str(id))
    await menu_service.delete_menu(id=id)
