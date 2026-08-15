import random
import uuid
from copy import deepcopy

from app.services.debate_service import DEBATE_TOPICS
from app.services.storage import load_json, save_json


DEFAULT_CRITERIA = [
    {
        "label": "Luận điểm",
        "max": 25,
        "keywords": ["quan điểm", "cho rằng", "theo em", "luận điểm"],
    },
    {
        "label": "Bằng chứng",
        "max": 25,
        "keywords": ["bằng chứng", "ví dụ", "dữ liệu", "nguồn", "nghiên cứu", "thực tế"],
    },
    {
        "label": "Suy luận",
        "max": 25,
        "keywords": ["vì", "do đó", "vì vậy", "nên", "nếu", "tuy nhiên"],
    },
    {
        "label": "Phản biện",
        "max": 15,
        "keywords": ["phản biện", "hạn chế", "rủi ro", "mặt trái", "ngoại lệ"],
    },
    {
        "label": "Độ rõ",
        "max": 10,
        "keywords": ["rõ ràng", "tóm lại", "kết luận"],
    },
]


def _default_topics():
    return [
        {
            "id": topic["id"],
            "title": topic["title"],
            "side_a": topic["side_a"],
            "side_b": topic["side_b"],
            "criteria": deepcopy(DEFAULT_CRITERIA),
        }
        for topic in DEBATE_TOPICS
    ]


DEFAULT_DEBATE_CONFIG = {
    "mode": "random",
    "fixed_topic_id": DEBATE_TOPICS[0]["id"],
    "priority_cursor": 0,
    "topics": _default_topics(),
}


def _normalize_config(data):
    config = deepcopy(DEFAULT_DEBATE_CONFIG)
    if isinstance(data, dict):
        config.update({key: value for key, value in data.items() if key in config})
    if config.get("mode") not in {"random", "priority", "fixed"}:
        config["mode"] = "random"
    topics = config.get("topics") if isinstance(config.get("topics"), list) else []
    config["topics"] = [normalize_topic(topic) for topic in topics if normalize_topic(topic)]
    if not config["topics"]:
        config["topics"] = _default_topics()
    topic_ids = {topic["id"] for topic in config["topics"]}
    if config.get("fixed_topic_id") not in topic_ids:
        config["fixed_topic_id"] = config["topics"][0]["id"]
    try:
        config["priority_cursor"] = int(config.get("priority_cursor", 0))
    except (TypeError, ValueError):
        config["priority_cursor"] = 0
    return config


def debate_config():
    return _normalize_config(load_json("debate_config.json", DEFAULT_DEBATE_CONFIG))


def save_debate_config(config):
    normalized = _normalize_config(config)
    save_json("debate_config.json", normalized)
    return normalized


def normalize_topic(topic):
    if not isinstance(topic, dict):
        return None
    title = str(topic.get("title") or "").strip()
    side_a = str(topic.get("side_a") or "").strip()
    side_b = str(topic.get("side_b") or "").strip()
    if not title or not side_a or not side_b:
        return None
    topic_id = str(topic.get("id") or "").strip() or uuid.uuid4().hex[:12]
    criteria = normalize_criteria(topic.get("criteria"))
    return {
        "id": topic_id,
        "title": title,
        "side_a": side_a,
        "side_b": side_b,
        "criteria": criteria,
    }


def normalize_criteria(criteria):
    if not isinstance(criteria, list):
        return deepcopy(DEFAULT_CRITERIA)
    normalized = []
    for item in criteria:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        if not label:
            continue
        try:
            max_points = int(item.get("max", 10))
        except (TypeError, ValueError):
            max_points = 10
        keywords = item.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [part.strip() for part in keywords.split(",")]
        keywords = [str(keyword).strip() for keyword in keywords if str(keyword).strip()]
        normalized.append({"label": label, "max": max(1, max_points), "keywords": keywords})
    return normalized or deepcopy(DEFAULT_CRITERIA)


def criteria_to_text(criteria):
    return "\n".join(
        f"{item['label']}|{item['max']}|{', '.join(item.get('keywords') or [])}"
        for item in normalize_criteria(criteria)
    )


def parse_criteria_text(text):
    criteria = []
    for line in str(text or "").splitlines():
        parts = [part.strip() for part in line.split("|")]
        if not parts or not parts[0]:
            continue
        label = parts[0]
        max_points = parts[1] if len(parts) > 1 else "10"
        keywords = parts[2] if len(parts) > 2 else ""
        criteria.append({"label": label, "max": max_points, "keywords": keywords})
    return normalize_criteria(criteria)


def upsert_debate_topic(form):
    config = debate_config()
    topic_id = str(form.get("topic_id") or "").strip()
    topic = normalize_topic(
        {
            "id": topic_id or uuid.uuid4().hex[:12],
            "title": form.get("title"),
            "side_a": form.get("side_a"),
            "side_b": form.get("side_b"),
            "criteria": parse_criteria_text(form.get("criteria")),
        }
    )
    if not topic:
        raise ValueError("Chủ đề cần có câu hỏi, phe ủng hộ và phe phản đối.")
    replaced = False
    for index, existing in enumerate(config["topics"]):
        if existing["id"] == topic["id"]:
            config["topics"][index] = topic
            replaced = True
            break
    if not replaced:
        config["topics"].append(topic)
    save_debate_config(config)
    return topic


def delete_debate_topic(topic_id):
    config = debate_config()
    if len(config["topics"]) <= 1:
        raise ValueError("Cần giữ lại ít nhất một chủ đề.")
    config["topics"] = [topic for topic in config["topics"] if topic["id"] != topic_id]
    if config.get("fixed_topic_id") == topic_id:
        config["fixed_topic_id"] = config["topics"][0]["id"]
    save_debate_config(config)


def update_debate_mode(mode, fixed_topic_id=None):
    config = debate_config()
    if mode not in {"random", "priority", "fixed"}:
        raise ValueError("Chế độ ra chủ đề không hợp lệ.")
    config["mode"] = mode
    if fixed_topic_id:
        config["fixed_topic_id"] = fixed_topic_id
    save_debate_config(config)


def get_topic(index=0):
    config = debate_config()
    topics = config["topics"]
    try:
        index = int(index)
    except (TypeError, ValueError):
        index = 0
    return topics[index % len(topics)]


def get_topic_index_by_id(topic_id):
    config = debate_config()
    for index, topic in enumerate(config["topics"]):
        if topic["id"] == topic_id:
            return index
    return 0


def allocate_debate_topic():
    config = debate_config()
    topics = config["topics"]
    if config["mode"] == "fixed":
        index = get_topic_index_by_id(config.get("fixed_topic_id"))
        return index, topics[index]
    if config["mode"] == "priority":
        index = config["priority_cursor"] % len(topics)
        config["priority_cursor"] = index + 1
        save_debate_config(config)
        return index, topics[index]
    index = random.randrange(len(topics))
    return index, topics[index]
