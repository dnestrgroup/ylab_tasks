from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.redis.cache_submenu import SubMenuService
from app.schemas.schemas import CreateSubMenuRequest, SubMenuResponse
from app.services.cache_invalidation import cache_invalidation

router = APIRouter()


################################
#      Endpoints for submenus  #
################################


@router.get(  # type: ignore
    '/api/v1/menus/{id}/submenus', response_model=list[SubMenuResponse], summary='Метод получения списка подменю'
)
async def get_submenus(id: int, db: AsyncSession = Depends(get_db)) -> list[SubMenuResponse]:
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.get_list_submenus(id_menu=id)
    return response


@router.get(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}',
    response_model=SubMenuResponse,
    summary='Метод получения подменю по id',
)
async def get_submenu(id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)) -> SubMenuResponse:
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.get_one_submenu_by_id(id_menu=id_menu, id_submenu=id_submenu)
    return response


@router.patch(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus/{id_submenu}', response_model=SubMenuResponse, summary='Метод обновления подменю'
)
async def patch_submenu(
    background_tasks: BackgroundTasks,
    id_menu: int,
    id_submenu: int,
    data: CreateSubMenuRequest,
    db: AsyncSession = Depends(get_db),
) -> SubMenuResponse:
    submenu_service = SubMenuService(db=db)
    response = await submenu_service.update_submenu(data=data, id_menu=id_menu, id_submenu=id_submenu)
    background_tasks.add_task(cache_invalidation, '/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu))
    return response


@router.post(  # type: ignore
    '/api/v1/menus/{id_menu}/submenus',
    response_model=SubMenuResponse,
    status_code=201,
    summary='Метод создания подменю',
)
async def create_submenu(
    data: CreateSubMenuRequest, id_menu: int, db: AsyncSession = Depends(get_db)
) -> SubMenuResponse:
    submenu_service = SubMenuService(db=db)
    return await submenu_service.create_submenu(data=data, id_menu=id_menu)


@router.delete('/api/v1/menus/{id_menu}/submenus/{id_submenu}', summary='Метод удаления подменю')  # type: ignore
async def delete_submenu(
    background_tasks: BackgroundTasks,
    id_menu: int,
    id_submenu: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    submenu_service = SubMenuService(db=db)
    background_tasks.add_task(cache_invalidation, '/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu))
    await submenu_service.delete_submenu(id_menu=id_menu, id_submenu=id_submenu)
