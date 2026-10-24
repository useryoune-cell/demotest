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
        "label": "Có xem xét góc nhìn khác",
        "keywords": ["góc nhìn", "quan điểm trái chiều", "mặt khác", "phản biện", "hạn chế"],
    },
    {
        "key": "evidence",
        "label": "Có yêu cầu bằng chứng",
        "keywords": ["bằng chứng", "dẫn chứng", "nguồn", "trích dẫn", "dữ liệu"],
    },
    {
        "key": "verification",
        "label": "Có yêu cầu kiểm chứng",
        "keywords": ["kiểm chứng", "đối chiếu", "nguồn tin cậy", "xác minh", "sai"],
    },
    {
        "key": "self_review",
        "label": "Có điều chỉnh kết luận",
        "keywords": ["tự phản biện", "điểm yếu", "thiếu sót", "cải thiện", "rủi ro"],
    },
]


def score_prompt(prompt, scenario_id=None):
    from app.services.learning_feedback import criterion, review_text, level
    scenario = next((s for s in PROMPT_SCENARIOS if s['id'] == scenario_id), None)
    review = review_text({'instruction': 'Đánh giá yêu cầu AI kiểm chứng, đưa bằng chứng, xét góc nhìn khác và điều chỉnh kết luận có điều kiện; kiểm tra yêu cầu cụ thể thay vì chỉ đếm từ khóa.', 'scenario': scenario},
                         {'prompt': str(prompt or '')}, [criterion(c['key'], c['label'], 25, _hint_for(c['key'], 0)) for c in RUBRIC], deadline_seconds=35)
    for row in review['rubric']:
        row['hint'] = row['feedback']
    score = sum(r['score'] for r in review['rubric'])
    return {**review, 'score': score, 'level': level(score), 'provisional': not review['ai_available'],
            'suggestion': review['feedback'] + ' ' + review['reflection']}


def _hint_for(key, score):
    if score >= 14:
        return "Ổn."
    hints = {
        "multi_perspective": "Thêm yêu cầu nêu quan điểm trái chiều hoặc hạn chế.",
        "evidence": "Thêm yêu cầu nêu nguồn, bằng chứng hoặc dữ liệu.",
        "verification": "Thêm yêu cầu kiểm chứng và đối chiếu nguồn.",
        "assumptions": "Thêm yêu cầu chỉ ra giả định và mức độ chắc chắn.",
        "self_review": "Yêu cầu AI điều chỉnh kết luận và nêu mức độ chắc chắn khi chưa đủ căn cứ.",
    }
    return hints.get(key, "Cần cụ thể hơn.")


def _overall_suggestion(results):
    weakest = min(results, key=lambda item: item["score"])
    return f"Điểm cần cải thiện nhất: {weakest['label']}. {weakest['hint']}"


def _normalize(value):
    text = unicodedata.normalize("NFD", value)
    return "".join(char for char in text if unicodedata.category(char) != "Mn")
