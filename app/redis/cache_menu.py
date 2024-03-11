import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rep_menu import RepositoriesMenus
from app.schemas.schemas import CreateMenuRequest, MenuResponse
from app.redis.confredis import redis_client

class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_list(self):
        cached_data = redis_client.get('/api/v1/menus')
        if cached_data:
            menus = json.loads(cached_data)
            res = [MenuResponse(**json.loads(menu)) for menu in menus]
            return res
        repo = RepositoriesMenus(self.db)
        menus = await repo.r_get_list()
        menus_for_redis = [menu.json() for menu in menus]
        redis_client.setex('/api/v1/menus', 60, json.dumps(menus_for_redis))
        return menus

    async def get_one_menu_by_id(self, id):
        cached_data = redis_client.get('/api/v1/menus/' + str(id))
        if cached_data:
            return MenuResponse(**json.loads(cached_data))
        repo = RepositoriesMenus(self.db)
        menu = await repo.r_get(id=id)
        if menu:
            redis_client.setex('/api/v1/menus/' + str(id), 60, menu.model_dump_json())
            return menu
        raise HTTPException(status_code=404, detail='menu not found')

    async def update_menu(self, id, data):
        repo = RepositoriesMenus(self.db)
        update_menu = await repo.r_update(id=id, data=data)
        response = MenuResponse(
            id=update_menu.id,
            title=update_menu.title,
            description=update_menu.description,
            submenus_count=0, dishes_count=0)
        redis_client.setex('/api/v1/menus/' + str(id), 60, response.model_dump_json())
        return response

    async def create_menu(self, data: CreateMenuRequest):
        repo = RepositoriesMenus(self.db)
        new_menu = await repo.r_create(data=data)
        redis_client.delete('/api/v1/menus')
        res = await repo.r_get(id=new_menu.id)
        response = MenuResponse(
            id=res.id,
            title=res.title,
            description=res.description,
            submenus_count=res.submenus_count if res.submenus_count > 0 else None,
            dishes_count=res.dishes_count if res.dishes_count > 0 else None)
        redis_client.setex('/api/v1/menus/' + str(response.id), 60, res.model_dump_json())
        return response

    async def delete_menu(self, id):
        repo = RepositoriesMenus(self.db)
        redis_client.delete('/api/v1/menus/' + str(id))
        redis_client.delete('/api/v1/menus')
        await repo.r_delete(id=id)