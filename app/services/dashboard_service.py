from app.services.student_store import student_activities


DEMO_STUDENT_USERNAME = "student01"


TEACHER_OVERVIEW = {
    "completion": 78,
    "dependency": 31,
    "pending_reviews": 14,
    "new_reflections": 96,
    "scope_name": "Tất cả học sinh",
    "skills": [
        ("Phân tích thông tin", 72),
        ("Đánh giá bằng chứng", 64),
        ("Phát hiện sai lệch", 69),
        ("Kiểm chứng đa nguồn", 58),
        ("Chất lượng lập luận", 61),
        ("Quan điểm đối lập", 55),
        ("Phán đoán độc lập", 63),
        ("Tự điều chỉnh", 76),
    ],
    "students": [
        {"name": "An", "progress": 82, "risk": "Thấp", "dependency": 24},
        {"name": "Bình", "progress": 61, "risk": "Vừa", "dependency": 42},
        {"name": "Chi", "progress": 74, "risk": "Thấp", "dependency": 28},
        {"name": "Dũng", "progress": 49, "risk": "Cần hỗ trợ", "dependency": 57},
    ],
    "reviews": [
        {"type": "Nguồn không tồn tại", "module": "Thám tử AI", "detail": "Trạm B"},
        {"type": "Lỗi sai bối cảnh", "module": "AI cố tình sai", "detail": "Cấp 4"},
        {"type": "Chủ đề tranh biện", "module": "Đấu trường lập luận", "detail": "Solo"},
    ],
    "common_errors": [
        "Tin câu trả lời có nguồn nghe thuyết phục nhưng chưa kiểm chứng.",
        "Thiếu phản biện đối với quan điểm ban đầu của chính mình.",
        "Viết prompt dài nhưng không yêu cầu nguồn hoặc mức độ chắc chắn.",
    ],
}

DEMO_DASHBOARD = {
    "progress": 42,
    "metrics": [
        {"key": "verification", "icon": "search-check", "label": "Kiểm chứng", "score": 68},
        {"key": "argument", "icon": "scale", "label": "Lập luận", "score": 61},
        {"key": "self_adjust", "icon": "refresh-cw", "label": "Tự điều chỉnh", "score": 74},
        {"key": "independence", "icon": "shield-question", "label": "Độ độc lập", "score": 57},
    ],
}

EMPTY_DASHBOARD = {
    "progress": 0,
    "metrics": [
        {"key": "verification", "icon": "search-check", "label": "Kiểm chứng", "score": 0},
        {"key": "argument", "icon": "scale", "label": "Lập luận", "score": 0},
        {"key": "self_adjust", "icon": "refresh-cw", "label": "Tự điều chỉnh", "score": 0},
        {"key": "independence", "icon": "shield-question", "label": "Độ độc lập", "score": 0},
    ],
}

PROFILE = {
    "student_name": "Bạn",
    "skills": [
        {"label": "Phân tích thông tin", "score": 72},
        {"label": "Đánh giá bằng chứng", "score": 64},
        {"label": "Phát hiện sai lệch", "score": 69},
        {"label": "Kiểm chứng đa nguồn", "score": 58},
        {"label": "Chất lượng lập luận", "score": 61},
        {"label": "Quan điểm đối lập", "score": 55},
        {"label": "Phán đoán độc lập", "score": 63},
        {"label": "Tự điều chỉnh", "score": 76},
    ],
    "timeline": [42, 48, 53, 57, 63, 67, 70],
    "common_errors": [
        "Dễ tin câu trả lời có văn phong chắc chắn.",
        "Còn thiếu nguồn kiểm chứng thứ hai.",
        "Ít nêu hạn chế trong quan điểm của mình.",
    ],
    "recommendations": [
        {"module": "Tin hay không tin?", "reason": "Luyện hiệu chỉnh độ tin cậy sau khi xem bằng chứng."},
        {"module": "Prompt phản biện", "reason": "Tăng yêu cầu nguồn, giả định và tự phản biện trong prompt."},
        {"module": "Bản đồ lập luận", "reason": "Củng cố quan hệ giữa luận điểm, bằng chứng và kết luận."},
    ],
}

EMPTY_PROFILE = {
    "student_name": "Bạn",
    "skills": [
        {"label": skill["label"], "score": 0}
        for skill in PROFILE["skills"]
    ],
    "timeline": [0, 0, 0, 0, 0, 0, 0],
    "common_errors": [],
    "recommendations": [
        {"module": "Chatbot Socratic", "reason": "Bắt đầu một phiên dễ tiếp cận để tạo dữ liệu học tập đầu tiên."},
        {"module": "Nhật ký phản tư AI", "reason": "Sau khi học, lưu lại điều em tự rút ra."},
    ],
}


VERIFICATION_MODULES = {
    "tin-hay-khong-tin",
    "tham-tu-ai",
    "ai-co-tinh-sai",
    "so-sanh-ba-cau-tra-loi",
}
ARGUMENT_MODULES = {
    "ban-do-lap-luan",
    "dau-truong-lap-luan",
    "prompt-phan-bien",
}


def _average(values):
    values = [int(value) for value in values if value is not None]
    return round(sum(values) / len(values)) if values else 0


def _student_scores(username):
    activities = student_activities(username, limit=200)
    verification_scores = [
        item.get("score")
        for item in activities
        if item.get("module") in VERIFICATION_MODULES and item.get("score") is not None
    ]
    argument_scores = [
        item.get("score")
        for item in activities
        if item.get("module") in ARGUMENT_MODULES and item.get("score") is not None
    ]
    reflection_count = sum(1 for item in activities if item.get("action") == "reflection")
    human_first = [
        int((item.get("payload") or {}).get("confidence") or 0)
        for item in activities
        if item.get("module") == "con-nguoi-truoc-ai-sau" and item.get("action") == "ai_answer"
    ]
    meaningful_modules = {
        item.get("module")
        for item in activities
        if item.get("action") not in {"avatar", "draft"} and item.get("module")
    }

    verification = _average(verification_scores)
    argument = _average(argument_scores)
    self_adjust = min(100, reflection_count * 25)
    independence = min(100, round(len(human_first) * 30 + (_average(human_first) * 0.4 if human_first else 0)))
    progress = min(100, round(len(meaningful_modules) * 100 / 8))

    return {
        "progress": progress,
        "verification": verification,
        "argument": argument,
        "self_adjust": self_adjust,
        "independence": independence,
        "activities": activities,
    }


def teacher_overview():
    return TEACHER_OVERVIEW


def student_dashboard(username):
    if username == DEMO_STUDENT_USERNAME:
        return DEMO_DASHBOARD

    scores = _student_scores(username)
    return {
        "progress": scores["progress"],
        "metrics": [
            {"key": "verification", "icon": "search-check", "label": "Kiểm chứng", "score": scores["verification"]},
            {"key": "argument", "icon": "scale", "label": "Lập luận", "score": scores["argument"]},
            {"key": "self_adjust", "icon": "refresh-cw", "label": "Tự điều chỉnh", "score": scores["self_adjust"]},
            {"key": "independence", "icon": "shield-question", "label": "Độ độc lập", "score": scores["independence"]},
        ],
    }


def student_profile(username=None):
    if username == DEMO_STUDENT_USERNAME:
        return PROFILE

    scores = _student_scores(username)
    profile = {
        **EMPTY_PROFILE,
        "skills": [dict(skill) for skill in EMPTY_PROFILE["skills"]],
        "timeline": [0, 0, 0, 0, 0, 0, scores["progress"]],
        "common_errors": list(EMPTY_PROFILE["common_errors"]),
        "recommendations": list(EMPTY_PROFILE["recommendations"]),
    }
    score_by_label = {
        "Phân tích thông tin": scores["verification"],
        "Đánh giá bằng chứng": scores["verification"],
        "Phát hiện sai lệch": scores["verification"],
        "Kiểm chứng đa nguồn": scores["verification"],
        "Chất lượng lập luận": scores["argument"],
        "Quan điểm đối lập": scores["argument"],
        "Phán đoán độc lập": scores["independence"],
        "Tự điều chỉnh": scores["self_adjust"],
    }
    for skill in profile["skills"]:
        skill["score"] = score_by_label.get(skill["label"], 0)
    if scores["activities"]:
        profile["common_errors"] = ["Dữ liệu đang được hình thành từ các bài học đã lưu."]
    return profile
