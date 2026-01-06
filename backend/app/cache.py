import json
from functools import lru_cache
from typing import Any, Awaitable, Callable, Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from .config import settings


TTL_MAP = {
    "calendar": settings.ttl_calendar,
    "event": settings.ttl_event_detail,
    "session_results": settings.ttl_session_results,
    "telemetry": settings.ttl_telemetry,
    "standings": settings.ttl_standings,
    "profiles": settings.ttl_profiles,
}


@lru_cache(maxsize=1)
def get_redis_client() -> Optional[Redis]:
    """Create a singleton async Redis client or None if disabled."""
    if not settings.redis_url:
        return None
    return Redis.from_url(settings.redis_url, decode_responses=True)


def cache_key(prefix: str, identifier: str | int) -> str:
    """Build a normalized cache key for Redis."""
    return f"f1:{prefix}:{identifier}"


async def get_cached(
    key: str, loader: Callable[[], Awaitable[Any]], ttl: int | None
) -> Any:
    """Fetch data from cache or compute/store via loader."""
    client = get_redis_client()
    if client:
        try:
            cached_value = await client.get(key)
            if cached_value:
                return json.loads(cached_value)
        except RedisError:
            client = None  # disable for the remainder of the request

    payload = await loader()

    if client:
        try:
            await client.set(key, json.dumps(payload, default=str), ex=ttl)
        except RedisError:
            pass
    return payload


async def prime_cache(key: str, payload: Any, ttl: int | None) -> None:
    """Prime Redis cache with precomputed payload."""
    client = get_redis_client()
    if not client:
        return
    try:
        await client.set(key, json.dumps(payload, default=str), ex=ttl)
    except RedisError:
        pass
