from app.services.base import BaseService
from app.schemas.cars import Cars, CarsAdd, CarsPatch
from app.models.comments import Comments
from app.models.cars import CarsOrm

class CarsService(BaseService):
    AVG_RATING_TTL_SECONDS = 3600

    @staticmethod
    def _avg_rating_key(car_id: int) -> str:
        return f"car:{car_id}:avg_rating"

    async def _get_avg_ratings_cached(self, car_ids: list[int]) -> dict[int, float]:
        """
        Возвращает {car_id: avg_rating} с приоритетом Redis.
        Если в Redis нет ключа — считает агрегацией в MongoDB и кеширует на 1 час.
        """
        if not car_ids:
            return {}

        # Если Redis не передали — считаем только из Mongo
        if not self.redis:
            return await self._get_avg_ratings_from_mongo_and_defaults(car_ids)

        keys = [self._avg_rating_key(cid) for cid in car_ids]
        try:
            cached_values = await self.redis.mget(keys)
        except Exception:
            # Redis недоступен -> fallback на Mongo (без кеша)
            return await self._get_avg_ratings_from_mongo_and_defaults(car_ids)

        result: dict[int, float] = {}
        missing_ids: list[int] = []

        for cid, raw in zip(car_ids, cached_values, strict=False):
            if raw is None:
                missing_ids.append(cid)
                continue
            try:
                if isinstance(raw, (bytes, bytearray)):
                    raw = raw.decode("utf-8")
                result[cid] = float(raw)
            except Exception:
                missing_ids.append(cid)

        if missing_ids:
            computed = await self._get_avg_ratings_from_mongo_and_defaults(missing_ids)
            for cid, avg in computed.items():
                try:
                    await self.redis.set(self._avg_rating_key(cid), str(avg), expire=self.AVG_RATING_TTL_SECONDS)
                except Exception:
                    # Если Redis отвалился между mget и set — просто не кешируем
                    pass
            result.update(computed)

        return result

    async def _get_avg_ratings_from_mongo_and_defaults(self, car_ids: list[int]) -> dict[int, float]:
        """
        Одна агрегация в MongoDB для списка product_id.
        Для авто без отзывов возвращает 0.
        """
        if not car_ids:
            return {}

        # Защита: если Mongo не передали, просто вернём нули
        if not self.mongo_db:
            return {cid: 0.0 for cid in car_ids}

        pipeline = [
            {"$match": {"product_id": {"$in": car_ids}}},
            {"$group": {"_id": "$product_id", "avg": {"$avg": "$rating"}}},
        ]
        computed: dict[int, float] = {}
        # Через "чистый" Motor: в вашей версии связки beanie/motor
        # beanie.AggregationQuery пытается await'ить aggregate(), что падает.
        coll = Comments.get_pymongo_collection()
        cursor = coll.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        for doc in docs:
            try:
                computed[int(doc["_id"])] = float(doc.get("avg") or 0)
            except Exception:
                continue

        # Заполняем отсутствующие нулями
        for cid in car_ids:
            computed.setdefault(cid, 0.0)

        return computed

    async def get_all_filtered(
        self,
        limit: int | None = None,
        offset: int | None = None,
        name: str | None = None,
        min_rating: float | None = None
    ):
        filters = []
        if name:
            # По заданию — поиск по названию. Делаем contains + case-insensitive.
            filters.append(CarsOrm.name.ilike(f"%{name}%"))

        sql_limit = limit if (limit and offset) else None
        sql_offset = (limit * (offset - 1)) if (limit and offset) else None

        cars = await self.db.cars.get_filtered(sql_limit, sql_offset, *filters)

        car_ids = [car.id for car in cars]
        avg_ratings = await self._get_avg_ratings_cached(car_ids)

        result: list[dict] = []
        for car in cars:
            avg_rating = avg_ratings.get(car.id, 0.0)
            if min_rating and avg_rating < float(min_rating):
                continue
            car_dict = car.model_dump()
            car_dict["avg_rating"] = avg_rating
            result.append(car_dict)

        return result
    # async def get_all(self, limit, offset):
    #     return await self.db.cars.get_all(limit, offset)
    async def get_car_by_id(self, id):
        return await self.db.cars.get_one_or_none(id=id)
    async def update_car(self, car_id: int, data: CarsPatch):
        car = await self.get_car_by_id(car_id)
        if not car:
            return {"error": "Машина не найдена"}
        await self.db.cars.edit(data, id=car_id)
        await self.db.commit()
        return {"success": True}

    async def delete_car(self, car_id: int):
        car = await self.get_car_by_id(car_id)
        if not car:
            return {"error": "Машина не найдена"}
        await self.db.cars.delete(id=car_id)
        await self.db.commit()
        return {"success": True}
    async def add_car(self, data: CarsAdd):
        car = await self.db.cars.add(data)
        await self.db.commit()
        return {"success": True, "car": car}
    
