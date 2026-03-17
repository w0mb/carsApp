from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.dependencies import DBDep, RedisDep
from app.models.cars import CarsOrm


router = APIRouter(prefix="/popular", tags=["Популярные автомобили"])


@router.get("")
async def get_popular_cars(
    db: DBDep,
    redis: RedisDep,
    limit: int = Query(10, ge=1, le=100, description="Сколько авто вернуть"),
):
    if not redis:
        return []

    try:
        pairs = await redis.zrevrange_withscores("popular:cars", 0, limit - 1)
    except Exception:
        return []
    if not pairs:
        return []

    ids: list[int] = []
    views_by_id: dict[int, int] = {}

    for member, score in pairs:
        if isinstance(member, (bytes, bytearray)):
            member = member.decode("utf-8")
        car_id = int(member)
        ids.append(car_id)
        views_by_id[car_id] = int(score)

    stmt = select(CarsOrm).where(CarsOrm.id.in_(ids))
    result = await db.session.execute(stmt)
    cars = result.scalars().all()
    cars_by_id = {c.id: c for c in cars}

    # Сохраняем порядок топа Redis
    payload: list[dict] = []
    for car_id in ids:
        car = cars_by_id.get(car_id)
        if not car:
            continue
        payload.append(
            {
                "id": car.id,
                "name": car.name,
                "brand": car.brand,
                "price": float(car.price),
                "views": views_by_id.get(car_id, 0),
            }
        )

    return payload

