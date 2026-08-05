# AI Critical Thinking Lab

Flask web app for the AI Critical Thinking Lab project.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`.

## Deploy on Render

This repo includes `render.yaml` for Render Blueprint deploys.

Render settings:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

Set these environment variables in Render:

```env
SECRET_KEY=<generate a strong secret>
DATA_DIR=/var/data
ADMIN_USERNAME=<admin username>
ADMIN_PASSWORD=<admin password>
GEMINI_API_KEYS=key1,key2,key3
GEMINI_MODEL=gemini-3.5-flash
GEMINI_TIMEOUT_SECONDS=45
GEMINI_KEY_COOLDOWN_SECONDS=60
```

The Blueprint mounts a 1 GB disk at `/var/data` so student accounts, teacher accounts, reports, reflections, activity logs, and uploaded avatars survive redeploys.

## Gemini Config

Put all valid keys in `.env` as a comma-separated list:

```env
GEMINI_API_KEYS=key1,key2,key3
GEMINI_MODEL=gemini-3.5-flash
```

The backend rotates keys per request, cools down a key after HTTP 429, disables invalid/auth-failed keys, and avoids logging raw key values.

## Gemini Test Page

Open:

```text
http://127.0.0.1:5000/app/gemini
```

Useful endpoints:

```text
GET  /api/gemini/status
POST /api/gemini/test
```

`POST /api/gemini/test` expects:

```json
{
  "prompt": "Write 3 Socratic questions."
}
```
