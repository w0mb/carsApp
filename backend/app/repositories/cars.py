from app.repositories.base import BaseRepository
from app.models.cars import CarsOrm
from app.repositories.mappers.cars import CarsDataMapper


class CarsRepository(BaseRepository):
    model = CarsOrm
    mapper = CarsDataMapper



