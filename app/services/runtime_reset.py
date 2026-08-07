from copy import deepcopy
from datetime import datetime, timezone

from app.services.auth_service import (
    DEFAULT_AUTH_DATA,
    DEFAULT_STUDENT_ACCOUNTS,
    DEFAULT_TEACHER_ACCOUNTS,
)
from app.services.dashboard_service import DEMO_STUDENT_USERNAME
from app.services.storage import load_json, save_json


RESET_VERSION = "student01-only-data-2026-08-07"


def _dedupe_by_username(items):
    deduped = []
    seen = set()
    for item in items:
        username = item.get("username")
        if not username or username in seen:
            continue
        seen.add(username)
        deduped.append(item)
    return deduped


def _ensure_defaults(items, defaults):
    usernames = {item.get("username") for item in items}
    for default in defaults:
        if default["username"] not in usernames:
            items.append(deepcopy(default))
            usernames.add(default["username"])
    return items


def _reset_auth_data():
    data = load_json("auth.json", DEFAULT_AUTH_DATA)
    teachers = _dedupe_by_username(data.setdefault("teachers", []))
    students = []

    for student in data.setdefault("students", []):
        username = student.get("username")
        if not username or student.get("anonymous") or str(username).startswith("guest-"):
            continue
        cleaned = dict(student)
        if username != DEMO_STUDENT_USERNAME:
            cleaned["avatar_filename"] = ""
        students.append(cleaned)

    data["teachers"] = _ensure_defaults(teachers, DEFAULT_TEACHER_ACCOUNTS)
    data["students"] = _ensure_defaults(_dedupe_by_username(students), DEFAULT_STUDENT_ACCOUNTS)
    data.setdefault("reports", [])
    save_json("auth.json", data)


def _keep_only_demo_student(filename):
    data = load_json(filename, {})
    demo_entries = data.get(DEMO_STUDENT_USERNAME)
    save_json(filename, {DEMO_STUDENT_USERNAME: demo_entries} if demo_entries else {})


def reset_non_demo_student_data_once():
    state = load_json("reset_state.json", {})
    if state.get("version") == RESET_VERSION:
        return False

    _reset_auth_data()
    _keep_only_demo_student("activity.json")
    _keep_only_demo_student("reflections.json")
    state["version"] = RESET_VERSION
    state["applied_at"] = datetime.now(timezone.utc).isoformat()
    save_json("reset_state.json", state)
    return True
