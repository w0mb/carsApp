from decimal import Decimal
from pydantic import BaseModel

from app.schemas.comments import CommentCreate


class CarsAdd(BaseModel):
    name: str
    brand: str
    description: str | None = None
    price: Decimal
    stock: int


class Cars(CarsAdd):
    id: int

class CarsGet(Cars):
    comments: list[CommentCreate] = []

class CarsPatch(BaseModel):
    name: str | None = None
    brand: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
