
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.comments import Comments

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    return db.client

async def connect():
    db.client = AsyncIOMotorClient(str(settings.MONGO_URL))
    await init_beanie(database=db.client[settings.MONGO_DB_NAME], document_models=[Comments])
async def close():

    db.client.close()
