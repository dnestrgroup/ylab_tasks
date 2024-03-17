from typing import Any

import pandas as pd
from sqlalchemy import delete, not_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Dishes, MainMenu, SubMenu


class UploadMenu:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run(self) -> None:
        df = pd.read_excel('app/admin/Menu.xlsx', engine='openpyxl')
        data = df.values.tolist()
        set_of_menus: set[str] = set()
        set_of_submenus: set[str] = set()
        set_of_dishes: set[str] = set()
        for i in data:
            # Если выбранная Excel-строка относится к Меню, то обрабатываем её здесь:
            if (not str(i[1]).isdigit()) and (str(i[1]) != 'nan'):
                last_idm = str(int(i[0]))
                data_menu: dict[str, Any] = {
                    'title': i[1],
                    'description': i[2],
                    'id_xls': str(int(i[0])),
                }
                query = (
                    insert(MainMenu)
                    .values(**data_menu)
                    .on_conflict_do_update(constraint='uq_main_menu_id_xls', set_=data_menu)
                    .returning(MainMenu.id)
                )
                main_menu_id = (await self.db.execute(query)).scalar()
                await self.db.commit()
                set_of_menus.add(str(i[1]))

            # Если выбранная Excel-строка относится к Подменю, то обрабатываем её здесь:
            if (str(i[1]).isdigit()) and (not str(i[2]).isdigit()) and (i[2] != 'nan'):
                last_idsm = str(int(i[1]))
                data_submenu = {
                    'title': i[2],
                    'description': i[3],
                    'main_menu_id': main_menu_id,
                    'id_xls': last_idm + str(int(i[1])),
                }
                query = (
                    insert(SubMenu)
                    .values(**data_submenu)
                    .on_conflict_do_update(constraint='uq_sub_menu_id_xls', set_=data_submenu)
                    .returning(SubMenu.id)
                )
                sub_menu_id = (await self.db.execute(query)).scalar()
                await self.db.commit()
                set_of_submenus.add(str(i[2]))

            # Если выбранная Excel-строка относится к Блюдам, то обрабатываем её здесь:
            if (str(i[2]).isdigit()) and (not str(i[3]).isdigit()) and (i[3] != 'nan'):
                data_dish = {
                    'title': i[3],
                    'description': i[4],
                    'price': i[5],
                    'sub_menu_id': sub_menu_id,
                    'id_xls': last_idm + last_idsm + str(int(i[2])),
                }
                query = (
                    insert(Dishes)
                    .values(**data_dish)
                    .on_conflict_do_update(constraint='uq_dish_id_xls', set_=data_dish)
                    .returning(Dishes.id)
                )
                (await self.db.execute(query)).scalar()
                await self.db.commit()
                set_of_dishes.add(str(i[3]))

        await self.db.execute(delete(MainMenu).where(not_(MainMenu.title.in_(set_of_menus))))
        await self.db.commit()
        await self.db.execute(delete(SubMenu).where(not_(SubMenu.title.in_(set_of_submenus))))
        await self.db.commit()
        await self.db.execute(delete(Dishes).where(not_(Dishes.title.in_(set_of_dishes))))
        await self.db.commit()
