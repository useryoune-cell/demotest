import json
import os
from copy import deepcopy


def data_dir():
    path = os.getenv("DATA_DIR") or os.path.join(os.getcwd(), "instance")
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
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)
