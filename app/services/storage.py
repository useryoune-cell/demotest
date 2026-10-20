import json
import os
import tempfile
import threading
from copy import deepcopy

_update_lock = threading.RLock()


def data_dir():
    from flask import current_app, has_app_context
    path = current_app.config.get("DATA_DIR") if has_app_context() else None
    path = path or os.getenv("DATA_DIR") or os.path.join(os.getcwd(), "instance")
    os.makedirs(path, exist_ok=True)
    return path


def data_path(filename):
    return os.path.join(data_dir(), filename)


def load_json(filename, default):
    path = data_path(filename)
    if not os.path.exists(path):
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return deepcopy(default)


def save_json(filename, data):
    path = data_path(filename)
    descriptor, temp_path = tempfile.mkstemp(dir=os.path.dirname(path), suffix='.tmp')
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def update_json(filename, default, mutate):
    """Serialize read/modify/write in the single-worker, threaded deployment."""
    with _update_lock:
        data = load_json(filename, default)
        result = mutate(data)
        save_json(filename, data)
        return result
