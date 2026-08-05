import unicodedata


DETECTIVE_STATIONS = [
    {
        "code": "A",
        "title": "Dữ kiện sai",
        "task": "Tìm dữ kiện sai trong câu trả lời AI.",
        "text": "Theo AI, Việt Nam hiện có hơn 120 triệu dân, nên mọi chính sách giáo dục trực tuyến phải ưu tiên mô hình lớp học đông trên 80 học sinh.",
        "error_type": "Dữ kiện sai",
        "suspicious_text": "hơn 120 triệu dân",
        "evidence": "Dân số Việt Nam chưa đạt 120 triệu; cần kiểm tra số liệu từ Tổng cục Thống kê hoặc nguồn quốc tế đáng tin cậy.",
        "rewrite": "Không nên suy luận chính sách từ một con số dân số chưa được kiểm chứng; cần dùng số liệu cập nhật và xem thêm điều kiện vùng miền, hạ tầng, giáo viên.",
    },
    {
        "code": "B",
        "title": "Nguồn không tồn tại",
        "task": "Kiểm tra nguồn được AI viện dẫn.",
        "text": "AI khẳng định báo cáo 'Global Classroom Automation Index 2026' của UNESCO cho thấy 73% trường học đã thay giáo viên bằng trợ lý AI.",
        "error_type": "Nguồn không tồn tại",
        "suspicious_text": "Global Classroom Automation Index 2026",
        "evidence": "Tên báo cáo có dấu hiệu bịa hoặc cần xác minh trên kho tài liệu chính thức của UNESCO trước khi trích dẫn.",
        "rewrite": "Chỉ nên viết rằng một số tổ chức quốc tế đang thảo luận về AI trong giáo dục, và phải dẫn đúng tên báo cáo, năm phát hành, đường dẫn kiểm chứng.",
    },
    {
        "code": "C",
        "title": "Suy luận thiếu căn cứ",
        "task": "Tìm kết luận vượt quá bằng chứng.",
        "text": "Một lớp thử dùng chatbot trong 2 tuần và điểm kiểm tra tăng nhẹ, vì vậy nhà trường có thể kết luận AI là nguyên nhân chính làm kết quả học tập cải thiện.",
        "error_type": "Suy luận thiếu căn cứ",
        "suspicious_text": "AI là nguyên nhân chính",
        "evidence": "Cần nhóm đối chứng, thời gian đủ dài và kiểm soát yếu tố khác trước khi kết luận quan hệ nhân quả.",
        "rewrite": "Kết quả tăng nhẹ chỉ cho thấy dấu hiệu cần nghiên cứu thêm; chưa đủ căn cứ để khẳng định AI là nguyên nhân chính.",
    },
    {
        "code": "D",
        "title": "Khái quát hóa quá mức",
        "task": "Tìm cụm từ tuyệt đối hóa.",
        "text": "Vì vài học sinh sao chép bài từ AI, tất cả học sinh dùng AI đều sẽ mất năng lực tự học nếu nhà trường không cấm hoàn toàn.",
        "error_type": "Khái quát hóa quá mức",
        "suspicious_text": "tất cả học sinh dùng AI đều sẽ mất năng lực tự học",
        "evidence": "Không thể lấy một số trường hợp vi phạm để kết luận về toàn bộ học sinh và mọi cách sử dụng AI.",
        "rewrite": "Một số học sinh có thể lệ thuộc vào AI nếu thiếu quy định; giải pháp nên kết hợp hướng dẫn sử dụng, kiểm chứng nguồn và đánh giá phần tự suy nghĩ.",
    },
    {
        "code": "E",
        "title": "Đúng nhưng sai bối cảnh",
        "task": "Tìm chi tiết đúng nhưng đặt sai bối cảnh.",
        "text": "AI có thể tóm tắt văn bản rất nhanh, nên trong mọi bài đọc hiểu, học sinh chỉ cần nộp bản tóm tắt do AI tạo là đủ thể hiện năng lực đọc.",
        "error_type": "Đúng nhưng sai bối cảnh",
        "suspicious_text": "đủ thể hiện năng lực đọc",
        "evidence": "Tóm tắt nhanh là một khả năng của AI, nhưng năng lực đọc hiểu còn gồm phân tích, suy luận, đối chiếu bằng chứng và diễn giải bằng lời của học sinh.",
        "rewrite": "AI có thể hỗ trợ tóm tắt, nhưng bài đọc hiểu vẫn cần phần phân tích, kiểm chứng và giải thích riêng của học sinh.",
    },
    {
        "code": "F",
        "title": "Thiên lệch",
        "task": "Tìm nhận định một chiều.",
        "text": "Trường học nên triển khai AI càng nhanh càng tốt vì công nghệ này chắc chắn giúp mọi học sinh học hiệu quả hơn và gần như không tạo ra rủi ro đáng kể.",
        "error_type": "Thiên lệch",
        "suspicious_text": "chắc chắn giúp mọi học sinh học hiệu quả hơn",
        "evidence": "Đánh giá chính sách AI cần xét cả lợi ích, điều kiện triển khai, chênh lệch truy cập, quyền riêng tư, gian lận và nguy cơ phụ thuộc.",
        "rewrite": "AI có thể hỗ trợ học tập nếu được thiết kế và giám sát tốt, nhưng nhà trường cần đánh giá cả lợi ích, rủi ro và điều kiện triển khai.",
    },
]

ARGUMENT_MAP = {
    "id": "ai-homework-map",
    "question": "Có nên cho phép học sinh sử dụng AI tạo sinh trong bài tập về nhà?",
    "source_text": "Có thể cho phép học sinh dùng AI trong bài tập về nhà nếu giáo viên đặt quy định rõ. AI có thể giúp tìm ý và giải thích khái niệm, nhưng học sinh phải ghi cách dùng, kiểm chứng nguồn và nộp phần tự suy nghĩ trước. Nếu không có quy định, học sinh dễ sao chép nguyên văn và giảm khả năng tự lập luận. Vì vậy, AI nên được dùng có kiểm soát thay vì cấm hoàn toàn hoặc thả tự do.",
    "buckets": [
        {"key": "claim", "label": "Luận điểm"},
        {"key": "evidence", "label": "Bằng chứng"},
        {"key": "assumption", "label": "Giả định"},
        {"key": "counter", "label": "Phản biện"},
        {"key": "conclusion", "label": "Kết luận"},
    ],
    "pieces": [
        {"id": "p1", "text": "Có thể cho phép học sinh dùng AI nếu giáo viên đặt quy định rõ.", "bucket": "claim"},
        {"id": "p2", "text": "AI có thể giúp tìm ý và giải thích khái niệm.", "bucket": "evidence"},
        {"id": "p3", "text": "Học sinh phải ghi cách dùng, kiểm chứng nguồn và nộp phần tự suy nghĩ trước.", "bucket": "assumption"},
        {"id": "p4", "text": "Nếu không có quy định, học sinh dễ sao chép nguyên văn.", "bucket": "counter"},
        {"id": "p5", "text": "AI nên được dùng có kiểm soát thay vì cấm hoàn toàn hoặc thả tự do.", "bucket": "conclusion"},
    ],
}


def get_detective_station(code="A"):
    code = str(code or "A").upper()
    for station in DETECTIVE_STATIONS:
        if station["code"] == code:
            return station
    return DETECTIVE_STATIONS[0]


def public_station(station):
    return {
        "code": station["code"],
        "title": station["title"],
        "task": station["task"],
        "text": station["text"],
    }


def score_detective(code, suspicious_text, error_type, explanation, evidence, rewrite):
    station = get_detective_station(code)
    suspicious = _normalize(str(suspicious_text or "").strip())
    expected_suspicious = _normalize(station["suspicious_text"])
    selected_type = _normalize(str(error_type or "").strip())
    expected_type = _normalize(station["error_type"])
    points = 0
    if expected_suspicious in suspicious or suspicious in expected_suspicious:
        points += 25
    if selected_type == expected_type:
        points += 25
    points += min(20, len(str(explanation or "").strip()) // 3)
    points += min(15, len(str(evidence or "").strip()) // 4)
    points += min(15, len(str(rewrite or "").strip()) // 5)
    return {
        "score": min(points, 100),
        "expected": station,
        "passed": points >= 60,
    }


def score_argument_map(placements):
    placements = placements or {}
    total = len(ARGUMENT_MAP["pieces"])
    correct = 0
    details = []
    for piece in ARGUMENT_MAP["pieces"]:
        actual = placements.get(piece["id"])
        is_correct = actual == piece["bucket"]
        correct += 1 if is_correct else 0
        details.append(
            {
                "piece_id": piece["id"],
                "expected": piece["bucket"],
                "actual": actual,
                "correct": is_correct,
            }
        )
    return {
        "score": round(correct / total * 100),
        "correct": correct,
        "total": total,
        "details": details,
    }


def _normalize(value):
    text = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")
