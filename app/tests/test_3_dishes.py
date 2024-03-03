import pytest

from app.tests.conftest import TestClientBase


class TestDishes(TestClientBase):

    @pytest.mark.asyncio
    async def test_post_menu(self):
        """
        создаем пункт главного меню
        и проверяем ответ что пункт меню создан
        """
        menu_title = "Drinks"
        menu_description="any description"
        data = {
                "title": menu_title,
                "description": menu_description,
               }
        response = await self.client.post("/menus", json=data)
        assert response.status_code == 201
        pytest.id_menu = response.json()["id"]
        pytest.menu_title = menu_title
        pytest.menu_description= menu_description
        assert response.json()["title"] == menu_title
        assert response.json()["description"] == menu_description
        assert response.json()["submenus_count"] == None
        assert response.json()["dishes_count"] == None




    @pytest.mark.asyncio
    async def test_post_sub_menu(self):
        """
        создаем пункт подменю в созданном ранее меню
        """
        sub_menu_title = "Cold"
        sub_menu_description="any submenu description"
        data = {
                "title": sub_menu_title,
                "description": sub_menu_description,
               }
        response = await self.client.post(f"/menus/{pytest.id_menu}/submenus", json=data)
        assert response.status_code == 201
        pytest.id_sub_menu = response.json()["id"]
        pytest.sub_menu_title = sub_menu_title
        pytest.sub_menu_description= sub_menu_description
        assert response.json()["title"] == sub_menu_title
        assert response.json()["description"] == sub_menu_description



    @pytest.mark.asyncio(depends=["TestDishes::test_post_menu", "TestDishes::test_post_sub_menu"])
    async def test_get_dishes(self):
        """
        просматриваем список блюд
        """
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes")
        assert response.status_code == 200
        assert response.json() ==[]

    

    @pytest.mark.asyncio
    async def test_post_dishes(self):
        """
        создаем блюдо
        """
        dish_title = "CocaCola"
        dish_description="any dish description"
        dish_price = 100.5
        data = {
                "title": dish_title,
                "description": dish_description,
                "price": dish_price
               }
        response = await self.client.post(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes", json=data)
        assert response.status_code == 201
        pytest.id_dish = response.json()["id"]
        pytest.dish_title = dish_title
        pytest.dish_description= dish_description
        pytest.dish_price= dish_price
        assert response.json()["title"] == dish_title
        assert response.json()["description"] == dish_description
        assert response.json()["price"] == f"{dish_price:.2f}"



    @pytest.mark.asyncio
    async def test_get_dishes_not_empty(self):
        """
        просмотр список блюд
        """
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes")
        assert response.status_code == 200
        assert response.json() != []


    @pytest.mark.asyncio()
    async def test_get_dish_by_id(self):
        """
        просмотр определенного блюда по id
        """
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes/{pytest.id_dish}")
        assert response.status_code == 200
        assert response.json()["title"] == pytest.dish_title
        assert response.json()["description"] == pytest.dish_description
        assert response.json()["price"] == f"{pytest.dish_price:.2f}"




    @pytest.mark.asyncio(depends=["TestDishes::test_post_menu", "TestDishes::test_post_sub_menu"])
    async def test_update_dish_by_id(self):
        """
        1. обновляем ранее созданное блюдо
        2. просматриваем только что созданное блюдо, что title description изменился на новое
        """
        new_dish_title = "updated submenu Cold"
        new_dish_description="updated submenu description"
        new_dish_price = 99.5
        data = {
                "title": new_dish_title,
                "description": new_dish_description,
                "price": new_dish_price
               }
        response = await self.client.patch(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes/{pytest.id_dish}", json=data)
        assert response.status_code == 200
        assert response.json()["title"] == new_dish_title
        assert response.json()["description"] == new_dish_description
        assert response.json()["price"] == f"{new_dish_price:.2f}"
        
        
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes/{pytest.id_dish}")
        assert response.status_code == 200
        assert response.json()["title"] == new_dish_title
        assert response.json()["description"] == new_dish_description
        assert response.json()["price"] == f"{new_dish_price:.2f}"




    @pytest.mark.asyncio(depends=["TestSubMenu::test_post_menu", "TestDishes::test_post_sub_menu"])
    async def test_delete_dish_by_id(self):
        """
        1. удаляем обновленное блюдо
        2. просматриваем список блюд
        3. просматриваем определенное блюдо и убеждаемся что его нет 404
        """
        response = await self.client.delete(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes/{pytest.id_dish}")
        assert response.status_code == 200
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes")
        assert response.status_code == 200
        assert response.json() == []
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes/{pytest.id_dish}")
        assert response.status_code == 404




    @pytest.mark.asyncio(depends=["TestSubMenu::test_post_menu"])
    async def test_delete_sub_menu_by_id(self):
        """
        1. удаляем подменю
        2. просматриваем список подменю
        """
        response = await self.client.delete(f"/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}")
        assert response.status_code == 200
        response = await self.client.get(f"/menus/{pytest.id_menu}/submenus")
        assert response.status_code == 200
        assert response.json() == []




    @pytest.mark.asyncio(depends=["TestMenu::test_post_menu"])
    async def test_delete_menu_by_id(self):
        """
        1. удаляем меню
        2. просматриваем список меню
        """
        response = await self.client.delete(f"/menus/{pytest.id_menu}")
        assert response.status_code == 200
        response = await self.client.get(f"/menus")
        assert response.status_code == 200
        assert response.json() == []
