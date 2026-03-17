from fastapi import APIRouter

# Импортируем роутер из index.py
from routers.index import front_router as index_router

# Создаем главный frontend роутер
front_router = APIRouter()

front_router.include_router(index_router)  # без префикса
