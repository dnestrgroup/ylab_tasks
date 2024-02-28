from typing import Optional
from pydantic import BaseModel


class CreateMenuRequest(BaseModel):
    title: str
    description: str


class MenuResponse(BaseModel):
    id: str
    title: str
    description: str
    submenus_count: Optional[int]
    dishes_count: Optional[int]


class CreateSubMenuRequest(BaseModel):
    title: str
    description: str


class SubMenuResponse(BaseModel):
    id: str
    title: str
    description: str
    dishes_count: Optional[int]


class CreateDishesRequest(BaseModel):
    title: str
    description: str
    price: float


class DishesResponse(BaseModel):
    id: str
    title: str
    description: str
    price: str