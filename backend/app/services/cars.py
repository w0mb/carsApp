from app.services.base import BaseService
from app.schemas.cars import Cars, CarsAdd, CarsPatch
from app.models.comments import Comments
from app.models.cars import CarsOrm
import logging

class CarsService(BaseService):
    AVG_RATING_TTL_SECONDS = 10
    _log = logging.getLogger("app.redis")

    @staticmethod
    def _avg_rating_key(car_id: int) -> str:
        return f"car:{car_id}:avg_rating"

    async def _get_avg_ratings_cached(self, car_ids: list[int]) -> dict[int, float]:
        if not car_ids:
            return {}

        if not self.redis:
            return await self._get_avg_ratings_from_mongo_and_defaults(car_ids)

        keys = [self._avg_rating_key(cid) for cid in car_ids]
        try:
            cached_values = await self.redis.mget(keys)
        except Exception:
            self._log.warning("avg_rating cache: redis mget failed, fallback to mongo")
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

        self._log.info(
            "avg_rating cache: hit=%s miss=%s total=%s",
            len(result),
            len(missing_ids),
            len(car_ids),
        )

        if missing_ids:
            computed = await self._get_avg_ratings_from_mongo_and_defaults(missing_ids)
            for cid, avg in computed.items():
                try:
                    await self.redis.set(self._avg_rating_key(cid), str(avg), expire=self.AVG_RATING_TTL_SECONDS)
                    self._log.info(
                        "avg_rating cache: set key=%s value=%s ttl=%s",
                        self._avg_rating_key(cid),
                        avg,
                        self.AVG_RATING_TTL_SECONDS,
                    )
                except Exception:
                    self._log.warning("avg_rating cache: set failed key=%s", self._avg_rating_key(cid))
                    pass
            result.update(computed)

        return result

    async def _get_avg_ratings_from_mongo_and_defaults(self, car_ids: list[int]) -> dict[int, float]:
        if not car_ids:
            return {}

        if not self.mongo_db:
            return {cid: 0.0 for cid in car_ids}

        pipeline = [
            {"$match": {"product_id": {"$in": car_ids}}},
            {"$group": {"_id": "$product_id", "avg": {"$avg": "$rating"}}},
        ]
        computed: dict[int, float] = {}
        coll = Comments.get_pymongo_collection()
        cursor = coll.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        for doc in docs:
            try:
                computed[int(doc["_id"])] = float(doc.get("avg") or 0)
            except Exception:
                continue

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
    
