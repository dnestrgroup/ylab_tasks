import pytest

from app.tests.conftest import TestClientBase


class TestAllMenu(TestClientBase):

    @pytest.mark.asyncio  # type: ignore
    async def test_get_all_structured_data(self) -> None:
        """
        1. Создаем меню и проверяем что меню создано
        2. Создаем подменю в созданном ранее меню и проверяем что подменю создано
        3. Создаем блюдо в созданном подменю и проверяем что блюдо создано
        4. Получаем все структурированные данные одним запросом
        5. Удаляем меню и каскадно все связаныее данные
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

        dish_title = 'CocaCola'
        dish_description = 'any dish description'
        dish_price = 100.5
        dish_price_s = str(dish_price)
        data = {'title': dish_title, 'description': dish_description, 'price': dish_price_s}
        response = await self.client.post(f'/menus/{pytest.id_menu}/submenus/{pytest.id_sub_menu}/dishes', json=data)
        assert response.status_code == 201
        pytest.id_dish = response.json()['id']
        pytest.dish_title = dish_title
        pytest.dish_description = dish_description
        pytest.dish_price = dish_price_s
        assert response.json()['title'] == dish_title
        assert response.json()['description'] == dish_description
        assert response.json()['price'] == f'{dish_price:.2f}'

        response = await self.client.get('/all')
        assert response.status_code == 200
        assert response.json() != []

        response = await self.client.get('/menus')
        for menu in response.json():
            await self.client.delete(f"/menus/{menu['id']}")
