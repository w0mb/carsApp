from typing import TypeVar
from pydantic import BaseModel
from app.database import Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)

class DataMapper:
    db_model: type[DBModelType] = None
    input_schema: type[SchemaType] | None = None  
    output_schema: type[SchemaType] | None = None  

    @classmethod
    def map_to_domain_entity(cls, data):
        
        schema = cls.output_schema or cls.input_schema
        return schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        return cls.db_model(**data.model_dump())