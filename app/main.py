from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import delete, func, insert, select, update
from app.db.base import get_db
from app.models.models import Dishes, MainMenu, SubMenu
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import CreateDishesRequest, CreateMenuRequest, CreateSubMenuRequest, DishesResponse, MenuResponse, SubMenuResponse

app = FastAPI(
    title="Complex menu"
)



################################
#      Endpoints for menus     #
################################
@app.get("/api/v1/menus", response_model=List[MenuResponse])
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


@app.get("/api/v1/menus/{id}", response_model=MenuResponse)
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


@app.post("/api/v1/menus", response_model=MenuResponse,  status_code=201)
async def create_menu(data: CreateMenuRequest, db: AsyncSession = Depends(get_db)) -> MenuResponse:
    query = (
        insert(MainMenu)
        .values(title=data.title, description=data.description)
        .returning(MainMenu.id, MainMenu.title, MainMenu.description)
    )
    result = (await db.execute(query)).fetchone()
    await db.commit()
    return MenuResponse(id=str(result[0]), title=result[1], description=result[2], submenus_count=None, dishes_count=None)


@app.patch("/api/v1/menus/{id}", response_model=MenuResponse)
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


@app.delete("/api/v1/menus/{id}")
async def delete_menu(id: int, db: AsyncSession = Depends(get_db)):
    query = delete(MainMenu).where(MainMenu.id == id)
    await db.execute(query)
    await db.commit()



################################
#      Endpoints for submenus  #
################################

@app.get("/api/v1/menus/{id}/submenus", response_model=List[SubMenuResponse])
async def get_submenus(id: int, db: AsyncSession = Depends(get_db)):
    query = select(SubMenu).filter(SubMenu.main_menu_id == id)
    list_menu = []
    for menu in (await db.execute(query)).scalars():
        list_menu.append(
            SubMenuResponse(id=str(menu.id), title=menu.title, description=menu.description, dishes_count=None)
        )
    return list_menu


@app.get(
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


@app.patch(
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


@app.post(
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


@app.delete("/api/v1/menus/{id_menu}/submenus/{id_submenu}")
async def delete_submenu(
    id_menu: int, id_submenu: int, db: AsyncSession = Depends(get_db)
):
    query = delete(SubMenu).where(SubMenu.id == id_submenu)
    await db.execute(query)
    await db.commit()



################################
#      Endpoints for dishes    #
################################

@app.get(
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


@app.get(
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


@app.patch(
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


@app.post(
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


@app.delete(
    "/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{id_dishes}",
)
async def delete_dishes(
    id_menu: int, id_submenu: int, id_dishes: int, db: AsyncSession = Depends(get_db)
):
    query = delete(Dishes).where(Dishes.id == id_dishes)
    await db.execute(query)
    await db.commit()