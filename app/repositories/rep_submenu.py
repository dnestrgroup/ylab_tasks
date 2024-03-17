from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Dishes, SubMenu
from app.schemas.schemas import CreateSubMenuRequest, SubMenuResponse


class RepositoriesSubMenus:
    def __init__(self, db: AsyncSession = None) -> None:
        self.db = db

    async def create(self, data: CreateSubMenuRequest, id_menu: int) -> SubMenuResponse:
        query = (
            insert(SubMenu)
            .values(title=data.title, description=data.description, main_menu_id=id_menu)
            .returning(SubMenu)
        )
        result = (await self.db.execute(query)).scalar_one()
        await self.db.commit()
        await self.db.refresh(result)
        return SubMenuResponse(id=str(result.id), title=result.title, description=result.description, dishes_count=None)

    async def get_list(self, id: int) -> list[SubMenuResponse]:
        query = select(SubMenu).filter(SubMenu.main_menu_id == id)
        list_submenus = []
        for submenu in (await self.db.execute(query)).scalars():
            list_submenus.append(
                SubMenuResponse(
                    id=str(submenu.id),
                    title=submenu.title,
                    description=submenu.description,
                    dishes_count=None,
                )
            )
        return list_submenus

    async def get(self, id_submenu: int) -> SubMenuResponse | None:
        query = select(SubMenu).filter(SubMenu.id == id_submenu)
        res = (await self.db.execute(query)).scalar_one_or_none()
        if res:
            dishes_query = select(func.count(Dishes.id)).where(Dishes.sub_menu_id == id_submenu)
            dishes_count = (await self.db.execute(dishes_query)).scalar()
            return SubMenuResponse(
                id=str(res.id),
                title=res.title,
                description=res.description,
                dishes_count=dishes_count,
            )
        return None

    async def update(self, id_submenu: int, data: CreateSubMenuRequest) -> SubMenuResponse:
        query = (
            update(SubMenu)
            .where(SubMenu.id == id_submenu)
            .values(title=data.title, description=data.description)
            .returning(SubMenu.id, SubMenu.title, SubMenu.description)
        )
        res = (await self.db.execute(query)).fetchone()
        await self.db.commit()
        return SubMenuResponse(id=str(res[0]), title=res[1], description=res[2], dishes_count=None)

    async def delete(self, id_submenu: int) -> None:
        query = delete(SubMenu).where(SubMenu.id == id_submenu)
        await self.db.execute(query)
        await self.db.commit()
