import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.confredis import redis_client
from app.repositories.rep_submenu import RepositoriesSubMenus
from app.schemas.schemas import CreateSubMenuRequest, SubMenuResponse


class SubMenuService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list_submenus(self, id_menu: int) -> list[SubMenuResponse]:
        cached_data = redis_client.get('/api/v1/menus/' + str(id_menu) + '/submenus')
        if cached_data:
            list_menu = json.loads(cached_data)
            return [SubMenuResponse(**json.loads(submenu)) for submenu in list_menu]
        repo_sm = RepositoriesSubMenus(self.db)
        list_menu = await repo_sm.get_list(id=id_menu)
        submenus_for_redis = [submenu.json() for submenu in list_menu]
        redis_client.setex('/api/v1/menus/{id_menu}/submenus', 60, json.dumps(submenus_for_redis))
        return list_menu

    async def get_one_submenu_by_id(self, id_menu: int, id_submenu: int) -> SubMenuResponse:
        cached_data = redis_client.get('/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu))
        if cached_data:
            return SubMenuResponse(**json.loads(cached_data))
        repo_sm = RepositoriesSubMenus(self.db)
        res = await repo_sm.get(id_submenu)
        if res:
            redis_client.setex('/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu), 1000, res.json())
            return res
        raise HTTPException(status_code=404, detail='submenu not found')

    async def update_submenu(self, data: CreateSubMenuRequest, id_menu: int, id_submenu: int) -> SubMenuResponse:
        repo_sm = RepositoriesSubMenus(self.db)
        res = await repo_sm.update(id_submenu, data)
        response_sm = SubMenuResponse(id=str(res.id), title=res.title, description=res.description, dishes_count=0)
        redis_client.setex('/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu), 1000, response_sm.json())
        return res

    async def create_submenu(self, data: CreateSubMenuRequest, id_menu: int) -> SubMenuResponse:
        repo_sm = RepositoriesSubMenus(self.db)
        res = await repo_sm.create(data, id_menu)
        if res:
            redis_client.delete(f'/api/v1/menus/{id_menu}/submenus')
            res.dishes_count = 0
            redis_client.setex(f'/api/v1/menus/{id_menu}/submenus/{res.id}', 1000, res.json())
        return res

    async def delete_submenu(self, id_menu: int, id_submenu: int) -> None:
        repo_sm = RepositoriesSubMenus(self.db)
        redis_client.delete(f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}')
        redis_client.delete(f'/api/v1/menus/{str(id_menu)}')
        await repo_sm.delete(id_submenu=id_submenu)
