

from app.repositories.base_mdb import MongoBaseRepository
from repositories.mappers.comments import CommentsDataMapper
from app.models.comments import Comments


class CommentsRepository(MongoBaseRepository):
    model = Comments
    mapper = CommentsDataMapper
