# F1 Desktop Pro

Professionelles F1 Daten-Analyse-Tool mit Sessions, Standings, Telemetrie und Export.

## Installation (Developer)

```
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python f1.py
```

## Lizenz

Die App nutzt eine lokale Lizenzpruefung mit einem kurzen Testzeitraum.
Fuer ein echtes kommerzielles Modell (Online-Aktivierung, Lizenzserver,
Abos, Team-Lizenzen) sollte ein separater Lizenzdienst integriert werden.

## Hinweise

- Cache und Logs liegen in `%APPDATA%\\F1DesktopPro`.
- Die Lizenzpruefung ist absichtlich einfach gehalten und dient als Platzhalter.

## Schnellstart Backend (FastAPI)

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. Optional `.env` im Projektwurzelverzeichnis anlegen (siehe `.env.example`):
   ```env
   FASTF1_CACHE_DIR=./.fastf1cache
   REDIS_URL=redis://localhost:6379/0
   TTL_CALENDAR=86400
   TTL_EVENT_DETAIL=28800
   TTL_SESSION_RESULTS=600
   TTL_TELEMETRY=172800
   TTL_STANDINGS=1800
   TTL_PROFILES=28800
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
3. API starten:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```
4. Health-Check: `http://localhost:8000/health`

### Backend per Docker

Falls du `--env-file .env` nutzt, erstelle vorher die Datei basierend auf `.env.example`.
```bash
docker build -t f1-api ./backend
docker run -p 8000:8000 --env-file .env f1-api
```

## Schnellstart Frontend (Next.js)

1. Wechsel in `frontend/` und installiere Abhängigkeiten:
   ```bash
   cd frontend
   npm install
   ```
2. Stelle sicher, dass `NEXT_PUBLIC_API_BASE_URL` gesetzt ist (Default `http://localhost:8000`).
3. Development-Server starten:
   ```bash
   npm run dev
   ```
