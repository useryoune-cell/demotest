from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json


REFLECTION_QUESTIONS = [
    "Ban đầu em nghĩ gì?",
    "AI đưa ra điều gì khác với suy nghĩ của em?",
    "Em tin phần nào trong phản hồi của AI?",
    "Em nghi ngờ phần nào?",
    "Em đã hoặc sẽ kiểm chứng bằng cách nào?",
    "Em có thay đổi quan điểm không? Vì sao?",
    "Nếu làm lại, em sẽ đặt câu hỏi khác như thế nào?",
]

DEFAULT_REFLECTION_DATA = {}


def _data():
    return load_json("reflections.json", DEFAULT_REFLECTION_DATA)


def _save(data):
    save_json("reflections.json", data)


def save_reflection(payload, username):
    data = _data()
    answers = payload.get("answers") or {}
    cleaned_answers = {
        str(index): str(value).strip()
        for index, value in answers.items()
        if str(value).strip()
    }
    entry = {
        "id": str(uuid4()),
        "student_username": username,
        "module": str(payload.get("module") or "unknown"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "answers": cleaned_answers,
        "context": payload.get("context") or {},
    }
    data.setdefault(username, []).append(entry)
    _save(data)
    return entry


def recent_reflections(username, limit=8):
    entries = _data().get(username, [])
    return list(reversed(entries[-limit:]))


def transfer_reflections(source_username, target_username):
    if not source_username or not target_username or source_username == target_username:
        return
    data = _data()
    entries = data.pop(source_username, [])
    for entry in entries:
        entry["student_username"] = target_username
    if entries:
        data.setdefault(target_username, []).extend(entries)
        _save(data)
