from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    MONGO_DB_NAME: str
    MONGO_USER: str | None = None
    MONGO_PASS: str | None = None
    MONGO_HOST: str
    MONGO_PORT: str

    REDIS_HOST: str
    REDIS_PORT: int
    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    @property
    def MONGO_URL(self):
        if self.MONGO_USER and self.MONGO_PASS:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"
    
    model_config = SettingsConfigDict(env_file=str(ENV_PATH))


settings = Settings()
