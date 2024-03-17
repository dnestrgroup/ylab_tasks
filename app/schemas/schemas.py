from pydantic import BaseModel


class CreateMenuRequest(BaseModel):
    title: str
    description: str


class MenuResponse(BaseModel):
    id: str
    title: str
    description: str
    submenus_count: int | None
    dishes_count: int | None


class CreateSubMenuRequest(BaseModel):
    title: str
    description: str


class SubMenuResponse(BaseModel):
    id: str
    title: str
    description: str
    dishes_count: int | None


class CreateDishesRequest(BaseModel):
    title: str
    description: str
    price: float


class DishesResponse(BaseModel):
    id: str
    title: str
    description: str
    price: str
