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


def teacher_overview():
    return TEACHER_OVERVIEW


def student_profile():
    return PROFILE
