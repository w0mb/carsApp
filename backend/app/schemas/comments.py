from datetime import datetime
from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    product_id: int
    author: str = "Аноним"
    text: str
    rating: int = Field(ge=1, le=5)

class CommentOut(CommentCreate):
    created_at: datetime
class CommentOutID(CommentOut):
    _id: str
class CommentUpdate(BaseModel):
    author: str | None = None
    text: str | None = None
    rating: int | None = None