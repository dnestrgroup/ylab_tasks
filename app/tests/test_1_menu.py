import pytest

from app.tests.conftest import TestClientBase


class TestMenu(TestClientBase):
    i = None

    @pytest.mark.asyncio
    async def test_clear_db(self):
        """
        чистим бд
        """
        response = await self.client.get("/menus")
        for menu in response.json():
            await self.client.delete(f"/menus/{menu['id']}")

    @pytest.mark.asyncio
    async def test_get_menu(self):
        """
        проверяем что нет созданных меню
        """
        response = await self.client.get("/menus")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_post_menu(self):
        """
        создаем пункт главного меню
        и проверяем ответ что пункт меню создан
        """
        menu_title = "Drinks"
        menu_description = "any description"
        data = {
            "title": menu_title,
            "description": menu_description,
        }
        response = await self.client.post("/menus", json=data)
        assert response.status_code == 201
        pytest.id_menu = response.json()["id"]
        pytest.menu_title = menu_title
        pytest.menu_description = menu_description
        assert response.json()["title"] == menu_title
        assert response.json()["description"] == menu_description
        assert response.json()["submenus_count"] == None
        assert response.json()["dishes_count"] == None

    @pytest.mark.asyncio(depends=["TestMenu::test_post_menu"])
    async def test_get_menu_by_id(self):
        """
        проверяем получение пункта меню по id
        """
        response = await self.client.get(f"/menus/{pytest.id_menu}")
        assert response.status_code == 200
        assert response.json()["title"] == pytest.menu_title
        assert response.json()["description"] == pytest.menu_description
        assert response.json()["submenus_count"] == 0
        assert response.json()["dishes_count"] == 0

    @pytest.mark.asyncio
    async def test_get_menu_not_empty(self):
        """
        проверяем что меню не пустое
        """
        response = await self.client.get("/menus")
        assert response.status_code == 200
        assert response.json() != []

    @pytest.mark.asyncio(depends=["TestMenu::test_post_menu"])
    async def test_update_menu_by_id(self):
        """
        1. обновляем ранее созданное меню
        2. просматриваем только что созданное меню, что title description изменился на новое
        """
        new_menu_title = "updated Drinks"
        new_menu_description = "updated description"
        data = {
            "title": new_menu_title,
            "description": new_menu_description,
        }
        response = await self.client.patch(f"/menus/{pytest.id_menu}", json=data)
        assert response.status_code == 200
        assert response.json()["title"] == new_menu_title
        assert response.json()["description"] == new_menu_description
        response = await self.client.get(f"/menus/{pytest.id_menu}")
        assert response.status_code == 200
        assert response.json()["title"] == new_menu_title
        assert response.json()["description"] == new_menu_description
        assert response.json()["submenus_count"] == 0
        assert response.json()["dishes_count"] == 0

    @pytest.mark.asyncio(depends=["TestMenu::test_post_menu"])
    async def test_delete_menu_by_id(self):
        """
        1. удаляем обновленное меню
        2. просматриваем список меню
        3. просматриваем определенное меню и убеждаемся что его нет 404
        """
        response = await self.client.delete(f"/menus/{pytest.id_menu}")
        assert response.status_code == 200
        response = await self.client.get(f"/menus")
        assert response.status_code == 200
        assert response.json() == []
        response = await self.client.get(f"/menus/{pytest.id_menu}")
        assert response.status_code == 404
