from collections import defaultdict
from app.services.base import BaseService
from app.schemas.cars import Cars, CarsAdd, CarsPatch

class CarsService(BaseService):
    async def get_all_filtered(
        self,
        limit: int,
        offset: int,
        name: str | None = None,
        min_rating: float | None = None
    ):
        cars = await self.db.cars.get_filtered(
            limit=limit,
            offset=limit * (offset - 1),
            name=name if name else None
        )

        if not cars:
            return [] 

        car_ids = [car.id for car in cars]

        comments = await self.mongo_db.comments.get_all(
    filter_query={"product_id": {"$in": car_ids}}
)

        ratings_map = defaultdict(list)
        for c in comments:
            ratings_map[c.product_id].append(c.rating)

        avg_ratings = {car_id: (sum(ratings_map[car_id]) / len(ratings_map[car_id])) if ratings_map[car_id] else 0
                       for car_id in car_ids}

        result = []
        for car in cars:
            avg_rating = avg_ratings.get(car.id, 0)
            if min_rating and avg_rating < min_rating:
                continue  # фильтруем по минимальному рейтингу
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
        return {"success": True}

    async def delete_car(self, car_id: int):
        car = await self.get_car_by_id(car_id)
        if not car:
            return {"error": "Машина не найдена"}
        await self.db.cars.delete(id=car_id)
        return {"success": True}
    async def add_car(self, data: CarsAdd):
        car = await self.db.cars.add(data)
        return {"success": True, "car": car}
    
