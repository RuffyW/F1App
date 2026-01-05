from __future__ import annotations

import asyncio
from datetime import datetime

from rq import Queue
from rq.worker import SimpleWorker
from redis import Redis

from backend.app.cache import TTL_MAP, cache_key, prime_cache
from backend.app.config import settings
from backend.app.services import get_calendar, get_session_results, get_telemetry


redis_client = Redis.from_url(settings.redis_url)
queue = Queue("prewarm", connection=redis_client)


def enqueue_prewarm() -> None:
    queue.enqueue(prewarm_next_event)


def prewarm_next_event() -> None:
    """Fetch next event payloads and persist them into Redis."""
    events = get_calendar(status="upcoming")
    if not events:
        return

    event = events[0]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_prime_event(event.id))
    loop.close()


async def _prime_event(event_id: str) -> None:
    classification_key = cache_key("session_results", f"classification:{event_id}-race")
    telemetry_key = cache_key("telemetry", f"{event_id}-race:top")
    await prime_cache(
        classification_key,
        [result.model_dump() for result in get_session_results(f"{event_id}-race")["classification"]],
        TTL_MAP["session_results"],
    )
    await prime_cache(
        telemetry_key,
        get_telemetry(f"{event_id}-race", drivers=["DRV1", "DRV2", "DRV3"]),
        TTL_MAP["telemetry"],
    )


def worker() -> None:
    """Start a simple RQ worker. Intended to be scheduled daily."""
    worker_instance = SimpleWorker([queue], connection=redis_client)
    worker_instance.work(with_scheduler=True)


if __name__ == "__main__":
    enqueue_prewarm()
