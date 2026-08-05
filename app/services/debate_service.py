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


def score_argument(text):
    text = str(text or "").strip()
    lowered = _normalize(text)
    words = [word for word in text.split() if word.strip()]

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

    total = min(100, claim + evidence + reasoning + counter + clarity)
    return {
        "total": total,
        "claim": claim,
        "evidence": evidence,
        "reasoning": reasoning,
        "counter": counter,
        "clarity": clarity,
    }


def _normalize(value):
    text = unicodedata.normalize("NFD", str(value or "").lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.replace("đ", "d")


def judge_debate(topic, player_argument, opponent_argument="", mode="solo"):
    player = score_argument(player_argument)
    opponent_text = opponent_argument or _sample_opponent_argument(topic)
    opponent = score_argument(opponent_text)

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

    weakest = min(
        [
            ("luận điểm", player["claim"]),
            ("bằng chứng", player["evidence"]),
            ("liên kết suy luận", player["reasoning"]),
            ("xem xét phản biện", player["counter"]),
            ("độ rõ", player["clarity"]),
        ],
        key=lambda item: item[1],
    )[0]
    return f"{result} Điểm cần cải thiện nhất: {weakest}."
