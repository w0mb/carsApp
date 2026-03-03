
from app.schemas.comments import CommentCreate, CommentOutID, CommentUpdate

from app.services.base import BaseService
from app.services.cars import CarsService

class CommentService(BaseService):
    async def add(self, data: CommentCreate):
        if await CarsService(self.db).get_car_by_id(data.product_id):
            return await self.mongo_db.comments.add(data)
        return {"error": "Машины с таким id нет"}

    async def get_all_filtered(self, limit: int, offset: int):
        return await self.mongo_db.comments.get_all(limit=limit, offset=offset * (limit - 1))

    async def get_comments_by_car_id(self, product_id: int):
        return await self.mongo_db.comments.get_all(filter_query={"product_id": product_id})

    async def update_comment(self, comment_id: str, data: CommentUpdate):
        existing = await self.mongo_db.comments.get_one(_id=comment_id)
        if not existing:
            return {"error": "Комментарий не найден"}
        await self.mongo_db.comments.edit(data, _id=comment_id)
        return {"success": True}

    async def delete_comment(self, comment_id: str):
        existing = await self.mongo_db.comments.get_one(_id=comment_id)
        if not existing:
            return {"error": "Комментарий не найден"}
        await self.mongo_db.comments.delete(_id=comment_id)
        return {"success": True}
    async def get_all_with_id(self, limit: int, offset: int):
        # Получаем raw объекты из Mongo
        entities = await self.mongo_db.comments.model.find().skip(offset).limit(limit).to_list()

        # Мапим вручную в CommentOutID
        result = [
            CommentOutID(
                _id=str(e.id),  # ObjectId -> str
                product_id=e.product_id,
                author=e.author,
                text=e.text,
                rating=e.rating,
                created_at=e.created_at
            )
            for e in entities
        ]
        return result