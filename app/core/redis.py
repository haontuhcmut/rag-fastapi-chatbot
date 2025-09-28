import redis.asyncio as aioredis

from app.config import Config


token_blocklist = aioredis.from_url(Config.BACKEND_URL)

async def add_jti_blocklist(jti:str) -> None:
    await token_blocklist.set(name=jti, value="", ex=3600)

async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    return jti is not None