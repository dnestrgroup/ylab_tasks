import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rep_dishes import RepositoriesDishes

from app.schemas.schemas import CreateDishesRequest, DishesResponse
from app.redis.confredis import redis_client

class DishesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list_dishes(self, id_menu: int, id_submenu: int) -> list[DishesResponse]:
        cached_data = redis_client.get(
            '/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu) + '/dishes')
        if cached_data:
            list_dishes = json.loads(cached_data)
            return [DishesResponse(**json.loads(dish)) for dish in list_dishes]
        repo_d = RepositoriesDishes(self.db)
        list_dishes = await repo_d.get_list(id_submenu)
        dishes_for_redis = [dish.json() for dish in list_dishes]
        redis_client.setex(
            '/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes', 1000, json.dumps(dishes_for_redis))
        return list_dishes

    async def get_one_dish_by_id(self, id_menu: int, id_submenu: int, id_dishes: int) -> DishesResponse:
        cached_data = redis_client.get(
            '/api/v1/menus/' + str(id_menu) + '/submenus/' + str(id_submenu) + '/dishes/' + str(id_dishes))
        if cached_data:
            return DishesResponse(**json.loads(cached_data))
        repo_d = RepositoriesDishes(self.db)
        res = await repo_d.get(id_menu, id_submenu, id_dishes)
        if res:
            redis_client.setex(
                f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}/dishes/{ str(id_dishes)}', 1000, res.json())
            return res
        raise HTTPException(status_code=404, detail='dish not found')

    async def update_dish(self, id_menu: int, id_submenu: int, id_dishes: int, data: CreateDishesRequest) -> DishesResponse:
        repo_d = RepositoriesDishes(self.db)
        res = await repo_d.update(id_menu, id_submenu, id_dishes, data)
        response_dish = DishesResponse(
            id=res.id,
            title=res.title,
            description=res.description,
            price=res.price
        )
        redis_client.setex(
            f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}/dishes/{str(id_dishes)}', 1000, response_dish.json())
        return res

    async def create_dish(self, data: CreateDishesRequest, id_menu: int, id_submenu: int) -> DishesResponse:
        repo_d = RepositoriesDishes(self.db)
        res = await repo_d.create(data, id_menu, id_submenu)
        if res:
            redis_client.delete(f'/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes')
            redis_client.setex(f'/api/v1/menus/{id_menu}/submenus/{id_submenu}/dishes/{res.id}', 1000, res.json())
        return res

    async def delete_dish(self, id_menu: int, id_submenu: int, id_dishes: int) -> None:
        repo_d = RepositoriesDishes(self.db)
        redis_client.delete(f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}/dishes/{str(id_dishes)}')
        redis_client.delete(f'/api/v1/menus/{str(id_menu)}/submenus/{str(id_submenu)}')
        await repo_d.delete(id_dishes=id_dishes)