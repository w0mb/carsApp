from beanie import Document, Indexed
from datetime import datetime
from typing import Annotated, Optional
from pydantic import Field

class Comments(Document):
    product_id: Annotated[int, Indexed()]
    author: str = "Аноним"
    text: str
    rating: int = Field(ge=1, le=5)  # от 1 до 5
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "comments"
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "author": "Иван",
                "text": "Отличный автомобиль!",
                "rating": 5,
                "created_at": "2024-01-01T12:00:00"
            }
        }