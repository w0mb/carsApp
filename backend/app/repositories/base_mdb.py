


from beanie import Document
from pydantic import BaseModel

from app.repositories.mappers.base import DataMapper


class MongoBaseRepository:
    model: type[Document]
    mapper: type[DataMapper]

    async def add(self, data: BaseModel):
        entity = self.mapper.map_to_persistence_entity(data)
        await entity.insert()
        return self.mapper.map_to_domain_entity(entity)
 
    async def get_one(self, **filter_by):
        entity = await self.model.find_one(filter_by)
        if not entity:
            return None
        return self.mapper.map_to_domain_entity(entity)
    async def get_all(self, limit: int | None = None, offset: int | None = None, filter_query: dict | None = None):
        query = self.model.find(filter_query or {})
        if offset:
            query = query.skip(offset)
        if limit:
            query = query.limit(limit)
        entities = await query.to_list()
        return [self.mapper.map_to_domain_entity(e) for e in entities]