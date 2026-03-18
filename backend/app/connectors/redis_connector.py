import logging

import redis.asyncio as redis


class RedisManager:
    _redis: redis.Redis

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def connect(self):
        logging.info(f"Начинаю подключение к Redis host={self.host}, port={self.port}")
        self._redis = redis.Redis(host=self.host, port=self.port, decode_responses=False)
        logging.info(f"Успешное подключение к Redis host={self.host}, port={self.port}")

    async def set(self, key: str, value: str, expire: int | None = None):
        if expire:
            await self._redis.set(key, value, ex=expire)
        else:
            await self._redis.set(key, value)

    async def get(self, key: str):
        return await self._redis.get(key)

    async def mget(self, keys: list[str]):
        if not keys:
            return []
        return await self._redis.mget(keys)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        return int(await self._redis.incrby(key, amount))

    async def zincrby(self, key: str, amount: int, member: str) -> float:
        return float(await self._redis.zincrby(key, amount, member))

    async def zrevrange_withscores(self, key: str, start: int, stop: int):
        return await self._redis.zrevrange(key, start, stop, withscores=True)

    async def close(self):
        if self._redis:
            await self._redis.close()