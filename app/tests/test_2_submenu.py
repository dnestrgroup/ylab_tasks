import pytest

from app.tests.conftest import TestClientBase


class TestSubMenu(TestClientBase):

    @pytest.mark.asyncio  # type: ignore
    async def test_post_menu(self) -> None:
        """
        создаем пункт главного меню
        и проверяем ответ что пункт меню создан
        """
        menu_title = 'Drinks'
        menu_description = 'any description'
        data = {
            'title': menu_title,
            'description': menu_description,
        }
        response = await self.client.post('/menus', json=data)
        assert response.status_code == 201
        pytest.id_menu = response.json()['id']
        pytest.menu_title = menu_title
        pytest.menu_description = menu_description
        assert response.json()['title'] == menu_title
        assert response.json()['description'] == menu_description
        assert response.json()['submenus_count'] == None  # noqa
        assert response.json()['dishes_count'] == None  # noqa

    @pytest.mark.asyncio(depends=['TestSubMenu::test_post_menu'])  # type: ignore
    async def test_get_sub_menus_in_menu(self) -> None:
        """
        получаем список подменю в Меню и убеждаемся что подменю пустое
        """
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus')
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio  # type: ignore
    async def test_post_sub_menu(self) -> None:
        """
        создаем пункт подменю в созданном ранее меню
        """
        sub_menu_title = 'Cold'
        sub_menu_description = 'any submenu description'
        data = {
            'title': sub_menu_title,
            'description': sub_menu_description,
        }
        response = await self.client.post(f'/menus/{pytest.id_menu}/submenus', json=data)
        assert response.status_code == 201
        pytest.id_sub_menu = response.json()['id']
        pytest.sub_menu_title = sub_menu_title
        pytest.sub_menu_description = sub_menu_description
        assert response.json()['title'] == sub_menu_title
        assert response.json()['description'] == sub_menu_description

    @pytest.mark.asyncio  # type: ignore
    async def test_get_sub_menu_not_empty(self) -> None:
        """
        проверяем что подменю не пустое
        """
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus')
        assert response.status_code == 200
        assert response.json() != []

    @pytest.mark.asyncio()  # type: ignore
    async def test_get_sub_menu_by_id(self) -> None:
        """
        проверяем получение пункта подменю по id
        """
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}')
        assert response.status_code == 200
        assert response.json()['title'] == pytest.sub_menu_title
        assert response.json()['description'] == pytest.sub_menu_description
        assert response.json()['dishes_count'] == 0

    @pytest.mark.asyncio(depends=['TestSubMenu::test_post_menu'])  # type: ignore
    async def test_update_sub_menu_by_id(self) -> None:
        """
        1. обновляем ранее созданное подменю
        2. просматриваем только что созданное подменю, что title description изменился на новое
        """
        new_sub_menu_title = 'updated submenu Cold'
        new_sub_menu_description = 'updated submenu description'
        data = {
            'title': new_sub_menu_title,
            'description': new_sub_menu_description,
        }
        response = await self.client.patch(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == new_sub_menu_title
        assert response.json()['description'] == new_sub_menu_description
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}')
        assert response.status_code == 200
        assert response.json()['title'] == new_sub_menu_title
        assert response.json()['description'] == new_sub_menu_description
        assert response.json()['dishes_count'] == 0

    @pytest.mark.asyncio(depends=['TestSubMenu::test_post_menu'])  # type: ignore
    async def test_delete_sub_menu_by_id(self) -> None:
        """
        1. удаляем обновленное подменю
        2. просматриваем список подменю
        3. просматриваем определенное подменю и убеждаемся что его нет 404
        """
        response = await self.client.delete(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}')
        assert response.status_code == 200
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus')
        assert response.status_code == 200
        assert response.json() == []
        response = await self.client.get(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}')
        assert response.status_code == 404

    @pytest.mark.asyncio(depends=['TestSubMenu::test_post_menu'])  # type: ignore
    async def test_delete_menu_by_id(self) -> None:
        """
        1. удаляем обновленное меню
        2. просматриваем список меню
        3. просматриваем определенное меню и убеждаемся что его нет 404
        """
        response = await self.client.delete(f'/menus/{pytest.id_menu}')
        assert response.status_code == 200
        response = await self.client.get('/menus')
        assert response.status_code == 200
        assert response.json() == []
        response = await self.client.get(f'/menus/{pytest.id_menu}')
        assert response.status_code == 404
