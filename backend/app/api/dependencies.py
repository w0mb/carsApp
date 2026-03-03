from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from app.database import async_session_maker
from app.utils.db_manager import DBManager
from app.utils.mongo_manager import MongoManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]
    per_page: Annotated[int | None, Query(10, ge=1, lt=30, description="Кол-во записей на странице")]


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