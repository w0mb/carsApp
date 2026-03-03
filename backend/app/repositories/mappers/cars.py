from app.repositories.mappers.base import DataMapper
from app.models.cars import CarsOrm
from app.schemas.cars import Cars, CarsAdd

class CarsDataMapper(DataMapper):
    db_model = CarsOrm
    input_schema = CarsAdd   # для добавления
    output_schema = Cars 