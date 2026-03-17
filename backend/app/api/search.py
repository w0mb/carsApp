from fastapi import APIRouter, Query
from app.api.dependencies import DBDep, MongoDep, PaginationDep, RedisDep
from app.services.cars import CarsService

router = APIRouter(prefix="/search", tags=["Поиск автомобилей"])

@router.get("")
async def search_cars(
    pagination: PaginationDep,
    db: DBDep,
    mongo: MongoDep,
    redis: RedisDep,
    name: str | None = Query(None, description="Название автомобиля для поиска"),
    min_rating: float | None = Query(None, ge=1, le=5, description="Минимальный рейтинг")
):
    if not name and not min_rating:
        return {"message": "Введите хотя бы один параметр для поиска (название или рейтинг)"}

    cars_service = CarsService(db=db, mongo_db=mongo, redis=redis)
    results = await cars_service.get_all_filtered(
        limit=pagination.per_page,
        offset=pagination.page,
        name=name,
        min_rating=min_rating
    )

    if not results:
        return {"message": "По вашему запросу автомобилей не найдено"}

    return results