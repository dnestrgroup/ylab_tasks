from typing import List
from fastapi import APIRouter, Depends,  HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse


router = APIRouter()

################################
#      Endpoints for menus     #
################################
@router.get("/api/v1/menus", response_model=List[MenuResponse])
async def get_menus(db: AsyncSession = Depends(get_db)):
    query = select(MainMenu)
    list_menu = []
    for menu in (await db.execute(query)).scalars():
        list_menu.append(
            MenuResponse(
                id=str(menu.id),
                title=menu.title,
                description=menu.description,
                submenus_count=None, 
                dishes_count=None,
            )
        )
    return list_menu


@router.get("/api/v1/menus/{id}", response_model=MenuResponse)
async def get_menu(id: int, db: AsyncSession = Depends(get_db)):
    query = select(MainMenu).filter(MainMenu.id == id)
    res = (await db.execute(query)).scalar_one_or_none()
    if res is not None:
        submenus_query = select(func.count(SubMenu.id)).where(
            SubMenu.main_menu_id == id
        )
        submenus_count = (await db.execute(submenus_query)).scalar()

        submenus = select(SubMenu.id).where(SubMenu.main_menu_id == id)
        submenus_results = await db.execute(submenus)
        submenu_ids = [result[0] for result in submenus_results]

        dishes_query = select(func.count(Dishes.id)).where(
            Dishes.sub_menu_id.in_(submenu_ids)
        )
        dishes_count = (await db.execute(dishes_query)).scalar()

        return MenuResponse(
            id=str(res.id),
            title=res.title,
            description=res.description,
            submenus_count=submenus_count,
            dishes_count=dishes_count,
        )
    raise HTTPException(status_code=404, detail="menu not found")


@router.post("/api/v1/menus", response_model=MenuResponse,  status_code=201)
async def create_menu(data: CreateMenuRequest, db: AsyncSession = Depends(get_db)) -> MenuResponse:
    query = (
        insert(MainMenu)
        .values(title=data.title, description=data.description)
        .returning(MainMenu.id, MainMenu.title, MainMenu.description)
    )
    result = (await db.execute(query)).fetchone()
    await db.commit()
    return MenuResponse(id=str(result[0]), title=result[1], description=result[2], submenus_count=None, dishes_count=None)


@router.patch("/api/v1/menus/{id}", response_model=MenuResponse)
async def patch_menu(
    id: int, data: CreateMenuRequest, db: AsyncSession = Depends(get_db)
):
    query = (
        update(MainMenu)
        .where(MainMenu.id == id)
        .values(title=data.title, description=data.description)
        .returning(MainMenu.id, MainMenu.title, MainMenu.description)
    )
    res = (await db.execute(query)).fetchone()
    await db.commit()
    return MenuResponse(id=str(res[0]), title=res[1], description=res[2], submenus_count=None, dishes_count=None)


@router.delete("/api/v1/menus/{id}")
async def delete_menu(id: int, db: AsyncSession = Depends(get_db)):
    query = delete(MainMenu).where(MainMenu.id == id)
    await db.execute(query)
    await db.commit()