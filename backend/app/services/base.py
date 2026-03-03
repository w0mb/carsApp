from app.utils.db_manager import DBManager
from app.utils.mongo_manager import MongoManager


class BaseService:
    db: DBManager | None
    mongo_db : MongoManager | None
    def __init__(
            self,
            db: DBManager | None = None,
            mongo_db: MongoManager | None = None
) -> None:
        self.db = db
        self.mongo_db = mongo_db