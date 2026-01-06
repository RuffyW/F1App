from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .cache import TTL_MAP, cache_key, get_cached
from .config import settings
from .services import (
    enable_fastf1_cache,
    get_calendar,
    get_event,
    get_profile,
    get_session_results,
    get_standings,
    get_telemetry,
)
from .timezone import localize_sessions

app = FastAPI(title="F1 App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def timezone_header(request: Request, call_next) -> Response:
    """Echo client timezone to help downstream localization."""
    response: Response = await call_next(request)
    tz = request.headers.get("x-client-timezone")
    if tz:
        response.headers["X-Client-Timezone"] = tz
    return response


@app.on_event("startup")
async def startup_event() -> None:
    enable_fastf1_cache(settings.fastf1_cache_dir)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/calendar")
async def calendar(
    status: str = Query("all", pattern="^(upcoming|completed|all)$")
) -> List[dict]:
    key = cache_key("calendar", status)
    return await get_cached(key, lambda: _calendar_payload(status), TTL_MAP["calendar"])


async def _calendar_payload(status: str) -> List[dict]:
    events = get_calendar(status)
    payload = []
    for event in events:
        sessions = localize_sessions(
            [session.model_dump() for session in event.sessions], event.timezone
        )
        payload.append(
            {
                "id": event.id,
                "season": event.season,
                "name": event.name,
                "circuit": event.circuit,
                "country": event.country,
                "start": event.start,
                "end": event.end,
                "timezone": event.timezone,
                "sessions": sessions,
            }
        )
    return payload


@app.get("/events/{event_id}")
async def event_detail(event_id: str) -> dict:
    key = cache_key("event", event_id)
    return await get_cached(key, lambda: _event_payload(event_id), TTL_MAP["event"])


async def _event_payload(event_id: str) -> dict:
    event = get_event(event_id)
    return {
        "id": event.id,
        "season": event.season,
        "name": event.name,
        "circuit": event.circuit,
        "country": event.country,
        "start": event.start,
        "end": event.end,
        "timezone": event.timezone,
        "sessions": localize_sessions(
            [session.model_dump() for session in event.sessions], event.timezone
        ),
    }


@app.get("/sessions/{session_id}/classification")
async def session_classification(session_id: str) -> List[dict]:
    key = cache_key("session_results", f"classification:{session_id}")
    return await get_cached(
        key,
        lambda: [result.model_dump() for result in get_session_results(session_id)["classification"]],
        TTL_MAP["session_results"],
    )


@app.get("/sessions/{session_id}/stints")
async def session_stints(session_id: str) -> List[dict]:
    key = cache_key("session_results", f"stints:{session_id}")
    return await get_cached(
        key,
        lambda: [result.model_dump() for result in get_session_results(session_id)["stints"]],
        TTL_MAP["session_results"],
    )


@app.get("/sessions/{session_id}/tyres")
async def session_tyres(session_id: str) -> List[dict]:
    key = cache_key("session_results", f"tyres:{session_id}")
    return await get_cached(
        key,
        lambda: [result.model_dump() for result in get_session_results(session_id)["tyres"]],
        TTL_MAP["session_results"],
    )


@app.get("/sessions/{session_id}/pitstops")
async def session_pitstops(session_id: str) -> List[dict]:
    key = cache_key("session_results", f"pitstops:{session_id}")
    return await get_cached(
        key,
        lambda: [result.model_dump() for result in get_session_results(session_id)["pitstops"]],
        TTL_MAP["session_results"],
    )


@app.get("/sessions/{session_id}/telemetry")
async def session_telemetry(session_id: str, drivers: Optional[str] = None) -> dict:
    driver_list = drivers.split(",") if drivers else []
    key = cache_key("telemetry", f"{session_id}:{','.join(driver_list)}")
    return await get_cached(
        key, lambda: get_telemetry(session_id, driver_list), TTL_MAP["telemetry"]
    )


@app.get("/standings/drivers")
async def driver_standings() -> dict:
    key = cache_key("standings", "drivers")
    return await get_cached(
        key, lambda: get_standings("drivers").model_dump(), TTL_MAP["standings"]
    )


@app.get("/standings/teams")
async def team_standings() -> dict:
    key = cache_key("standings", "teams")
    return await get_cached(
        key, lambda: get_standings("teams").model_dump(), TTL_MAP["standings"]
    )


@app.get("/drivers/{driver_id}")
async def driver_profile(driver_id: str) -> dict:
    key = cache_key("profiles", f"driver:{driver_id}")
    return await get_cached(key, lambda: get_profile(driver_id, "driver"), TTL_MAP["profiles"])


@app.get("/teams/{team_id}")
async def team_profile(team_id: str) -> dict:
    key = cache_key("profiles", f"team:{team_id}")
    return await get_cached(key, lambda: get_profile(team_id, "team"), TTL_MAP["profiles"])


@app.on_event("startup")
async def schedule_preload() -> None:
    """Placeholder for background warmup tasks."""
    # Attach more elaborate scheduling here (APScheduler/Celery worker).
    return None
