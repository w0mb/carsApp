from datetime import date

from fastapi import APIRouter, Query, Body, HTTPException

from app.api.dependencies import DBDep, MongoDep, PaginationDep
from app.services.cars import CarsService
from app.schemas.cars import CarsAdd, CarsGet, CarsPatch
from app.services.comments import CommentService

router = APIRouter(
    prefix="/cars",
    tags=["Автомобили"]
)
@router.post("/new")
async def create_car(db: DBDep, data: CarsAdd = Body(...)):
    return await CarsService(db).add_car(data)
@router.get("")
async def get_all_cars(
    pagination: PaginationDep,
    db: DBDep,
    mongo: MongoDep,
    name: str | None = Query(None, description="Название автомобиля для поиска"),
    rating: float | None = Query(None, description="Рейтинг автомобиля для поиска")
):

    return await CarsService(db, mongo).get_all_filtered(
        pagination.per_page,
        pagination.page,
        name,
    )

@router.get("/{car_id}")
async def get_one_car_by_id(
    car_id: int,
    db: DBDep,
    mongo: MongoDep
):
    car = await CarsService(db).get_car_by_id(car_id)
    comments = await CommentService(mongo_db=mongo).get_comment_by_car_id(car_id)
    res = CarsGet(
    id=car.id,
    name=car.name,
    brand=car.brand,
    description=car.description,
    price=float(car.price),
    stock=car.stock,
    comments=comments
)
    return res

@router.put("/{car_id}")
async def update_car(car_id: int, data: CarsPatch, db: DBDep):
    return await CarsService(db).update_car(car_id, data)

@router.delete("/{car_id}")
async def delete_car(car_id: int, db: DBDep):
    return await CarsService(db).delete_car(car_id)
