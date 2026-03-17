from fastapi import APIRouter

from app.schemas.comments import CommentCreate, CommentOutID, CommentUpdate
from app.services.comments import CommentService
from app.api.dependencies import DBDep, MongoDep, PaginationDep, RedisDep

router = APIRouter(prefix="/comments", tags=["Отзывы"])

@router.post("")
async def create_comment(data: CommentCreate, mongo: MongoDep, dbDep: DBDep, redis: RedisDep):
    return await CommentService(dbDep, mongo, redis).add(data)

@router.get("")
async def get_comments(mongo: MongoDep, pagDep: PaginationDep):
    return await CommentService(mongo_db=mongo).get_all_filtered(pagDep.per_page, pagDep.page)

@router.get("/product/{product_id}")
async def get_comments_by_car(product_id: int, mongo: MongoDep):
    return await CommentService(mongo_db=mongo).get_comments_by_car_id(product_id)

@router.put("/{comment_id}")
async def update_comment(comment_id: str, data: CommentUpdate, mongo: MongoDep):
    return await CommentService(mongo_db=mongo).update_comment(comment_id, data)

@router.delete("/{comment_id}")
async def delete_comment(comment_id: str, mongo: MongoDep):
    return await CommentService(mongo_db=mongo).delete_comment(comment_id)
@router.get("/with-id")
async def get_comments_with_id(mongo: MongoDep, pagDep: PaginationDep):
    return await CommentService(mongo_db=mongo).get_all_with_id(pagDep.per_page, pagDep.page)