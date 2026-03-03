from app.repositories.mappers.base import DataMapper
from app.models.comments import Comments
from app.schemas.comments import CommentCreate, CommentOut

class CommentsDataMapper(DataMapper):
    db_model = Comments
    input_schema = CommentCreate
    output_schema = CommentOut

    