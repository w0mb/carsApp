from app.utils.db_manager import DBManager
from app.utils.mongo_manager import MongoManager
from app.connectors.redis_connector import RedisManager


class BaseService:
    db: DBManager | None
    mongo_db : MongoManager | None
    redis: RedisManager | None
    def __init__(
            self,
            db: DBManager | None = None,
            mongo_db: MongoManager | None = None,
            redis: RedisManager | None = None,
) -> None:
        self.db = db
        self.mongo_db = mongo_db
        self.redis = redis