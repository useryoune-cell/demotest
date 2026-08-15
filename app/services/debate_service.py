import unicodedata


DEBATE_TOPICS = [
    {
        "id": "ai-homework",
        "title": "Có nên cho phép học sinh sử dụng AI tạo sinh trong tất cả bài tập về nhà?",
        "side_a": "Cho phép có điều kiện",
        "side_b": "Không nên cho phép rộng rãi",
    },
    {
        "id": "phone-school",
        "title": "Trường học có nên cấm điện thoại trong toàn bộ thời gian ở trường?",
        "side_a": "Nên cấm để tập trung",
        "side_b": "Không nên cấm tuyệt đối",
    },
    {
        "id": "electric-bus",
        "title": "Thành phố nên ưu tiên xe buýt điện hơn mở rộng đường cho xe cá nhân?",
        "side_a": "Ưu tiên giao thông công cộng xanh",
        "side_b": "Cần cân bằng với hạ tầng hiện tại",
    },
]

RANKS = [
    {"name": "Đồng", "min": 0, "color": "#b66a32"},
    {"name": "Bạc", "min": 100, "color": "#c7d2e0"},
    {"name": "Vàng", "min": 200, "color": "#f0c86a"},
    {"name": "Kim Cương", "min": 300, "color": "#69d8ff"},
    {"name": "Cao Thủ", "min": 400, "color": "#ff5fd2"},
]


def get_topic(index=0):
    try:
        index = int(index)
    except (TypeError, ValueError):
        index = 0
    return DEBATE_TOPICS[index % len(DEBATE_TOPICS)]


def get_rank(points):
    current = RANKS[0]
    for rank in RANKS:
        if points >= rank["min"]:
            current = rank
    return current


def score_argument(text, criteria=None):
    text = str(text or "").strip()
    lowered = _normalize(text)
    words = [word for word in text.split() if word.strip()]

    if criteria:
        return _score_by_teacher_criteria(lowered, words, criteria)

    claim = min(25, max(0, len(words) // 2))
    evidence_keywords = [
        "vi",
        "boi",
        "bang chung",
        "vi du",
        "du lieu",
        "nghien cuu",
        "thuc te",
        "nguon",
        "quy dinh",
        "khai niem",
    ]
    evidence = min(25, sum(1 for keyword in evidence_keywords if keyword in lowered) * 6)
    reasoning_keywords = ["do do", "vi vay", "nen", "tuy nhien", "mat khac", "neu", "can", "de", "tranh", "cho rang"]
    reasoning = min(25, sum(1 for keyword in reasoning_keywords if keyword in lowered) * 5)
    counter_keywords = ["phan bien", "han che", "rui ro", "ngoai le", "khong phai", "mat trai", "tuy nhien", "phu thuoc"]
    counter = min(20, sum(1 for keyword in counter_keywords if keyword in lowered) * 6)
    clarity = min(10, len(words) // 5)

    rubric_scores = [
        {"label": "Luận điểm", "score": claim, "max": 25},
        {"label": "Bằng chứng", "score": evidence, "max": 25},
        {"label": "Suy luận", "score": reasoning, "max": 25},
        {"label": "Phản biện", "score": counter, "max": 20},
        {"label": "Độ rõ", "score": clarity, "max": 10},
    ]
    total = min(100, claim + evidence + reasoning + counter + clarity)
    return {
        "total": total,
        "claim": claim,
        "evidence": evidence,
        "reasoning": reasoning,
        "counter": counter,
        "clarity": clarity,
        "rubric_scores": rubric_scores,
    }


def _score_by_teacher_criteria(lowered, words, criteria):
    rubric_scores = []
    raw_total = 0
    max_total = 0
    for item in criteria:
        label = str(item.get("label") or "").strip() or "Tiêu chí"
        try:
            max_points = int(item.get("max", 10))
        except (TypeError, ValueError):
            max_points = 10
        max_points = max(1, max_points)
        keywords = [
            _normalize(keyword)
            for keyword in (item.get("keywords") or [])
            if str(keyword or "").strip()
        ]
        keyword_score = sum(1 for keyword in keywords if keyword in lowered) * max(2, max_points // 4)
        length_score = min(max_points, max(0, len(words) // 8))
        score = min(max_points, keyword_score + length_score)
        rubric_scores.append({"label": label, "score": score, "max": max_points})
        raw_total += score
        max_total += max_points

    total = round((raw_total / max_total) * 100) if max_total else 0
    return {
        "total": min(100, total),
        "claim": rubric_scores[0]["score"] if len(rubric_scores) > 0 else 0,
        "evidence": rubric_scores[1]["score"] if len(rubric_scores) > 1 else 0,
        "reasoning": rubric_scores[2]["score"] if len(rubric_scores) > 2 else 0,
        "counter": rubric_scores[3]["score"] if len(rubric_scores) > 3 else 0,
        "clarity": rubric_scores[4]["score"] if len(rubric_scores) > 4 else 0,
        "rubric_scores": rubric_scores,
    }


def _normalize(value):
    text = unicodedata.normalize("NFD", str(value or "").lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.replace("đ", "d")


def judge_debate(topic, player_argument, opponent_argument="", mode="solo"):
    criteria = topic.get("criteria") or []
    player = score_argument(player_argument, criteria=criteria)
    opponent_text = opponent_argument or _sample_opponent_argument(topic)
    opponent = score_argument(opponent_text, criteria=criteria)

    if player["total"] == opponent["total"]:
        winner = "draw"
        delta = 0
    elif player["total"] > opponent["total"]:
        winner = "player"
        delta = 20
    else:
        winner = "opponent"
        delta = -30 if mode == "solo" else 0

    return {
        "topic": topic,
        "mode": mode,
        "player": player,
        "opponent": opponent,
        "opponent_argument": opponent_text,
        "winner": winner,
        "rank_delta": delta,
        "feedback": _feedback(player, opponent, winner),
        "criteria": criteria,
        "rubric_scores": player.get("rubric_scores", []),
    }


def _sample_opponent_argument(topic):
    return (
        f"Tôi nghiêng về hướng '{topic['side_b']}'. "
        "Học sinh có thể phụ thuộc vào công cụ và bỏ qua quá trình tự suy nghĩ. "
        "Cách dùng AI trong lớp học cần được xem xét cẩn thận hơn."
    )


def _feedback(player, opponent, winner):
    if winner == "player":
        result = "Bạn thắng vì lập luận có cấu trúc và điểm số rubric cao hơn."
    elif winner == "opponent":
        result = "Bạn thua sát nút; lập luận cần thêm bằng chứng hoặc phản biện rõ hơn."
    else:
        result = "Hai bên hòa; lập luận có chất lượng tương đương."

    rubric_scores = player.get("rubric_scores") or []
    weakest = min(
        [(item.get("label", "tiêu chí"), item.get("score", 0)) for item in rubric_scores],
        key=lambda item: item[1],
    )[0] if rubric_scores else "lập luận"
    return f"{result} Điểm cần cải thiện nhất: {weakest}."
