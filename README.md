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
