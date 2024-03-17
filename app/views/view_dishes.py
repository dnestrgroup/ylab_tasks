from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.redis.cache_dishes import DishesService
from app.schemas.schemas import CreateDishesRequest, DishesResponse
from app.services.cache_invalidation import cache_invalidation

router = APIRouter()


################################
#      Endpoints for dishes    #
################################


@router.get(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes',
    response_model=list[DishesResponse],
    summary='Метод получения списка блюд',
)
async def get_dishes(id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)) -> list[DishesResponse]:
    dishes_service = DishesService(db=db)
    response = await dishes_service.get_list_dishes(id_menu=id_menu, id_submenu=id_submenu)
    return response


@router.get(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}',
    response_model=DishesResponse,
    summary='Метод получения блюда по id',
)
async def get_dish(id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)) -> DishesResponse:
    dishes_service = DishesService(db=db)
    response = await dishes_service.get_one_dish_by_id(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes)
    return response


@router.patch(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}',
    response_model=DishesResponse,
    summary='Метод обновления блюда',
)
async def patch_dish(
    background_tasks: BackgroundTasks,
    id_menu: int,
    id_submenu: int,
    id_dishes: int,
    data: CreateDishesRequest,
    db: AsyncSession = Depends(get_db),
) -> DishesResponse:
    dishes_service = DishesService(db=db)
    response = await dishes_service.update_dish(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes, data=data)
    background_tasks.add_task(
        cache_invalidation,
        f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}/dishes/{str(id_dishes)}',
    )
    return response


@router.post(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes',
    response_model=DishesResponse,
    status_code=201,
    summary='Метод создания блюда',
)
async def create_dish(
    data: CreateDishesRequest,
    id_menu: int,
    id_submenu: int,
    db: AsyncSession = Depends(get_db),
) -> DishesResponse | None:
    submenu_service = DishesService(db=db)
    return await submenu_service.create_dish(data=data, id_menu=id_menu, id_submenu=id_submenu)


@router.delete(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}',
    summary='Метод удаления блюда',
)
async def delete_dishes(
    background_tasks: BackgroundTasks,
    id_menu: int,
    id_submenu: int,
    id_dishes: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    submenu_service = DishesService(db=db)
    background_tasks.add_task(
        cache_invalidation,
        f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}/dishes/{str(id_dishes)}',
    )
    await submenu_service.delete_dish(id_menu=id_menu, id_submenu=id_submenu, id_dishes=id_dishes)
