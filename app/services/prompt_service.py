import unicodedata


PROMPT_SCENARIOS = [
    {
        "id": "check-ai-history",
        "title": "Kiểm chứng câu trả lời lịch sử",
        "task": "Viết prompt yêu cầu AI tự kiểm tra một câu trả lời về Cách mạng tháng Tám năm 1945.",
    },
    {
        "id": "balanced-ai-policy",
        "title": "Đánh giá chính sách dùng AI",
        "task": "Viết prompt yêu cầu AI phân tích nhiều góc nhìn về việc dùng AI trong bài tập về nhà.",
    },
]

RUBRIC = [
    {
        "key": "multi_perspective",
        "label": "Đa góc nhìn",
        "keywords": ["góc nhìn", "quan điểm trái chiều", "mặt khác", "phản biện", "hạn chế"],
    },
    {
        "key": "evidence",
        "label": "Bằng chứng",
        "keywords": ["bằng chứng", "dẫn chứng", "nguồn", "trích dẫn", "dữ liệu"],
    },
    {
        "key": "verification",
        "label": "Kiểm chứng",
        "keywords": ["kiểm chứng", "đối chiếu", "nguồn tin cậy", "xác minh", "sai"],
    },
    {
        "key": "assumptions",
        "label": "Giả định",
        "keywords": ["giả định", "điều chưa biết", "chưa chắc", "mức độ chắc chắn"],
    },
    {
        "key": "self_review",
        "label": "Tự đánh giá",
        "keywords": ["tự phản biện", "điểm yếu", "thiếu sót", "cải thiện", "rủi ro"],
    },
]


def score_prompt(prompt):
    raw_text = str(prompt or "").strip().lower()
    text = _normalize(raw_text)
    results = []
    total = 0
    for criterion in RUBRIC:
        hits = sum(1 for keyword in criterion["keywords"] if _normalize(keyword) in text)
        length_bonus = 1 if len(text.split()) >= 24 else 0
        score = min(20, hits * 7 + length_bonus * 3)
        total += score
        results.append(
            {
                "key": criterion["key"],
                "label": criterion["label"],
                "score": score,
                "max": 20,
                "hint": _hint_for(criterion["key"], score),
            }
        )

    return {
        "score": min(total, 100),
        "rubric": results,
        "suggestion": _overall_suggestion(results),
    }


def _hint_for(key, score):
    if score >= 14:
        return "Ổn."
    hints = {
        "multi_perspective": "Thêm yêu cầu nêu quan điểm trái chiều hoặc hạn chế.",
        "evidence": "Thêm yêu cầu nêu nguồn, bằng chứng hoặc dữ liệu.",
        "verification": "Thêm yêu cầu kiểm chứng và đối chiếu nguồn.",
        "assumptions": "Thêm yêu cầu chỉ ra giả định và mức độ chắc chắn.",
        "self_review": "Thêm yêu cầu AI tự phản biện câu trả lời của chính nó.",
    }
    return hints.get(key, "Cần cụ thể hơn.")


def _overall_suggestion(results):
    weakest = min(results, key=lambda item: item["score"])
    return f"Điểm cần cải thiện nhất: {weakest['label']}. {weakest['hint']}"


def _normalize(value):
    text = unicodedata.normalize("NFD", value)
    return "".join(char for char in text if unicodedata.category(char) != "Mn")
