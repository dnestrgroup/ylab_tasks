from typing import List
from fastapi import APIRouter, Depends,  HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse


router = APIRouter()


################################
#      Endpoints for dishes    #
################################

@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes",
    response_model=List[DishesResponse],
)
async def get_dishes(db: AsyncSession = Depends(get_db)):
    query = select(Dishes)
    list_dishes = []
    for dishes in (await db.execute(query)).scalars():
        list_dishes.append(
            DishesResponse(
                id=str(dishes.id),
                title=dishes.title,
                description=dishes.description,
                price=str(dishes.price),
            )
        )
    return list_dishes


@router.get(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
    response_model=DishesResponse,
)
async def get_dish(
    id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)
):
    query = select(Dishes).filter(Dishes.id == id_dishes)
    res = (await db.execute(query)).scalar_one_or_none()
    if res is not None:
        return DishesResponse(
            id=str(res.id), title=res.title, description=res.description, price=str(res.price)
        )
    raise HTTPException(status_code=404, detail="dish not found")


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
    query = (
        update(Dishes)
        .where(Dishes.id == id_dishes)
        .values(title=data.title, description=data.description, price=data.price)
        .returning(Dishes.id, Dishes.title, Dishes.description, Dishes.price)
    )
    res = (await db.execute(query)).fetchone()
    await db.commit()
    return DishesResponse(id=str(res[0]), title=res[1], description=res[2], price=str(res[3]))


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
    query = (
        insert(Dishes)
        .values(
            title=data.title,
            description=data.description,
            sub_menu_id=id_submenu,
            price=data.price,
        )
        .returning(Dishes.id, Dishes.title, Dishes.description, Dishes.price)
    )
    result = (await db.execute(query)).fetchone()
    await db.commit()
    return DishesResponse(
        id=str(result[0]), title=result[1], description=result[2], price=str(result[3])
    )


@router.delete(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
)
async def delete_dishes(
    id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)
):
    query = delete(Dishes).where(Dishes.id == id_dishes)
    await db.execute(query)
    await db.commit()