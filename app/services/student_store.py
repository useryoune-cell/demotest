from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json

DEFAULT_ACTIVITY_DATA = {}


def _data():
    return load_json("activity.json", DEFAULT_ACTIVITY_DATA)


def _save(data):
    save_json("activity.json", data)


def record_student_activity(username, module, action, score=None, payload=None):
    if not username:
        return None
    data = _data()
    entry = {
        "id": str(uuid4()),
        "module": str(module or "unknown"),
        "action": str(action or "activity"),
        "score": score,
        "payload": payload or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault(username, []).append(entry)
    _save(data)
    return entry


def student_activities(username, limit=20):
    return list(reversed(_data().get(username, [])[-limit:]))


def transfer_student_activity(source_username, target_username):
    if not source_username or not target_username or source_username == target_username:
        return
    data = _data()
    entries = data.pop(source_username, [])
    if entries:
        data.setdefault(target_username, []).extend(entries)
        _save(data)
