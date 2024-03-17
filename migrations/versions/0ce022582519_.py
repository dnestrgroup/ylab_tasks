"""empty message

Revision ID: 0ce022582519
Revises: d605dbb26927
Create Date: 2024-03-16 14:17:10.921941

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0ce022582519'
down_revision: str | None = 'd605dbb26927'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dishes', sa.Column('id_xls', sa.String(), nullable=True))
    op.create_unique_constraint('uq_dish_id_xls', 'dishes', ['id_xls'])
    op.add_column('main_menu', sa.Column('id_xls', sa.String(), nullable=True))
    op.create_unique_constraint('uq_main_menu_id_xls', 'main_menu', ['id_xls'])
    op.add_column('sub_menu', sa.Column('id_xls', sa.String(), nullable=True))
    op.create_unique_constraint('uq_sub_menu_id_xls', 'sub_menu', ['id_xls'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_sub_menu_id_xls', 'sub_menu', type_='unique')
    op.drop_column('sub_menu', 'id_xls')
    op.drop_constraint('uq_main_menu_id_xls', 'main_menu', type_='unique')
    op.drop_column('main_menu', 'id_xls')
    op.drop_constraint('uq_dish_id_xls', 'dishes', type_='unique')
    op.drop_column('dishes', 'id_xls')
    # ### end Alembic commands ###
