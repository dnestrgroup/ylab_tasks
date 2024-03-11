from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from app.db.base import Base


class MainMenu(Base):
    __tablename__ = "main_menu"
    id:int = Column(Integer, primary_key=True)
    title:str = Column(String, nullable=False)
    description:str = Column(String, nullable=False)


class SubMenu(Base):
    __tablename__ = "sub_menu"
    id:int = Column(Integer, primary_key=True)
    title:str = Column(String, nullable=False)
    description:str = Column(String, nullable=False)
    main_menu_id:int = Column(
        Integer, ForeignKey("main_menu.id", ondelete="CASCADE"), nullable=False
    )


class Dishes(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    sub_menu_id = Column(
        Integer, ForeignKey("sub_menu.id", ondelete="CASCADE"), nullable=False
    )
    price = Column(Numeric(precision=18, scale=2), nullable=True)