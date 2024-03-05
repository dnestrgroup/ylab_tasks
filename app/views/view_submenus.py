from typing import List
from fastapi import APIRouter, Depends,  HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse


router = APIRouter()


################################
#      Endpoints for submenus  #
################################

@router.get("/api/v1/menus/{id}/submenus", response_model=List[SubMenuResponse])
async def get_submenus(id: int, db: AsyncSession = Depends(get_db)):
    query = select(SubMenu).filter(SubMenu.main_menu_id == id)
    list_menu = []
    for menu in (await db.execute(query)).scalars():
        list_menu.append(
            SubMenuResponse(id=str(menu.id), title=menu.title, description=menu.description, dishes_count=None)
        )
    return list_menu


@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}", response_model=SubMenuResponse
)
async def get_submenu(
    id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)
):
    query = select(SubMenu).filter(SubMenu.id == id_submenu)
    res = (await db.execute(query)).scalar_one_or_none()
    if res is not None:
        dishes_query = select(func.count(Dishes.id)).where(
            Dishes.sub_menu_id == id_submenu
        )
        dishes_count = (await db.execute(dishes_query)).scalar()
        return SubMenuResponse(
            id=str(res.id),
            title=res.title,
            description=res.description,
            dishes_count=dishes_count,
        )
    raise HTTPException(status_code=404, detail="submenu not found")


@router.patch(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}", response_model=SubMenuResponse
)
async def patch_submenu(
    id_menu: int,
    id_submenu: int,
    data: CreateSubMenuRequest,
    db: AsyncSession = Depends(get_db),
):
    query = (
        update(SubMenu)
        .where(SubMenu.id == id_submenu)
        .values(title=data.title, description=data.description)
        .returning(SubMenu.id, SubMenu.title, SubMenu.description)
    )
    res = (await db.execute(query)).fetchone()
    await db.commit()
    return SubMenuResponse(id=str(res[0]), title=res[1], description=res[2], dishes_count=None)


@router.post(
    "/api/v1/menus/{id_menu}/submenus", response_model=SubMenuResponse, status_code=201
)
async def create_submenu(
    data: CreateSubMenuRequest, id_menu: int, db: AsyncSession = Depends(get_db)
) -> SubMenuResponse:
    query = (
        insert(SubMenu)
        .values(title=data.title, description=data.description, main_menu_id=id_menu)
        .returning(SubMenu.id, SubMenu.title, SubMenu.description)
    )
    result = (await db.execute(query)).fetchone()
    await db.commit()
    return SubMenuResponse(id=str(result[0]), title=result[1], description=result[2], dishes_count=None)


@router.delete("/api/v1/menus/{id_menu}/submenus/{id_submenu}")
async def delete_submenu(
    id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)
):
    query = delete(SubMenu).where(SubMenu.id == id_submenu)
    await db.execute(query)
    await db.commit()