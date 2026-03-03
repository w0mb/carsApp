from fastapi import APIRouter

from app.api.cars import router as cars_router
from app.api.comments import router as comment_router
from app.api.search import router as search_router

api_router = APIRouter()

api_router.include_router(cars_router)
api_router.include_router(comment_router)
api_router.include_router(search_router)