from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from app.database import async_session_maker
from app.utils.db_manager import DBManager
from app.utils.mongo_manager import MongoManager
from app.init import redis_manager
from app.connectors.redis_connector import RedisManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(ge=1, description="Номер страницы", default=None)] = None
    per_page: Annotated[int | None, Query(ge=1, lt=30, description="Кол-во записей на странице", default=None)] = None


PaginationDep = Annotated[PaginationParams, Depends()]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)

async def get_mongo():
    async with MongoManager() as mongo:
        yield mongo

MongoDep = Annotated[MongoManager, Depends(get_mongo)]

async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_redis():
    # redis_manager подключается/закрывается в lifespan (main.py)
    yield redis_manager


RedisDep = Annotated[RedisManager, Depends(get_redis)]