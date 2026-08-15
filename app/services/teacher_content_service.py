import unicodedata
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json


ARGUMENT_BUCKETS = [
    {"key": "claim", "label": "Luận điểm"},
    {"key": "evidence", "label": "Bằng chứng"},
    {"key": "assumption", "label": "Giả định"},
    {"key": "counter", "label": "Phản biện"},
    {"key": "conclusion", "label": "Kết luận"},
]

DEFAULT_ARGUMENT_PACKAGES = [
    {
        "id": "argument-ai-homework-map",
        "title": "AI trong bài tập về nhà",
        "teacher_username": "teacher01",
        "teacher_name": "Giáo viên phản biện",
        "question": "Có nên cho phép học sinh sử dụng AI tạo sinh trong bài tập về nhà?",
        "source_text": "Có thể cho phép học sinh dùng AI trong bài tập về nhà nếu giáo viên đặt quy định rõ. AI có thể giúp tìm ý và giải thích khái niệm, nhưng học sinh phải ghi cách dùng, kiểm chứng nguồn và nộp phần tự suy nghĩ trước. Nếu không có quy định, học sinh dễ sao chép nguyên văn và giảm khả năng tự lập luận. Vì vậy, AI nên được dùng có kiểm soát thay vì cấm hoàn toàn hoặc thả tự do.",
        "pieces": [
            {"id": "p1", "text": "Có thể cho phép học sinh dùng AI nếu giáo viên đặt quy định rõ.", "bucket": "claim"},
            {"id": "p2", "text": "AI có thể giúp tìm ý và giải thích khái niệm.", "bucket": "evidence"},
            {"id": "p3", "text": "Học sinh phải ghi cách dùng, kiểm chứng nguồn và nộp phần tự suy nghĩ trước.", "bucket": "assumption"},
            {"id": "p4", "text": "Nếu không có quy định, học sinh dễ sao chép nguyên văn.", "bucket": "counter"},
            {"id": "p5", "text": "AI nên được dùng có kiểm soát thay vì cấm hoàn toàn hoặc thả tự do.", "bucket": "conclusion"},
        ],
        "active": True,
        "created_at": "demo",
    },
    {
        "id": "argument-source-check-map",
        "title": "Kiểm chứng nguồn khi dùng AI",
        "teacher_username": "teacher01",
        "teacher_name": "Giáo viên phản biện",
        "question": "Học sinh nên làm gì trước khi đưa thông tin AI vào bài thuyết trình?",
        "source_text": "Học sinh có thể dùng AI để gợi ý dàn ý, nhưng không nên đưa số liệu vào bài nếu chưa kiểm chứng. Một thông tin đáng dùng cần có nguồn rõ, được đối chiếu với ít nhất một nguồn độc lập và phù hợp với yêu cầu của giáo viên. Nếu AI đưa ra nguồn mơ hồ, học sinh cần ghi lại phần nghi ngờ và tìm tài liệu chính thống hơn. Vì vậy, kiểm chứng nguồn là bước bắt buộc trước khi trình bày.",
        "pieces": [
            {"id": "p1", "text": "Học sinh có thể dùng AI để gợi ý dàn ý.", "bucket": "claim"},
            {"id": "p2", "text": "Một thông tin đáng dùng cần có nguồn rõ và được đối chiếu với nguồn độc lập.", "bucket": "evidence"},
            {"id": "p3", "text": "Thông tin phải phù hợp với yêu cầu của giáo viên.", "bucket": "assumption"},
            {"id": "p4", "text": "Nếu AI đưa ra nguồn mơ hồ, học sinh cần ghi lại phần nghi ngờ.", "bucket": "counter"},
            {"id": "p5", "text": "Kiểm chứng nguồn là bước bắt buộc trước khi trình bày.", "bucket": "conclusion"},
        ],
        "active": True,
        "created_at": "demo-extra",
    },
]

DEFAULT_DETECTIVE_CASES = [
    {
        "id": "detective-station-a",
        "code": "A",
        "title": "Dữ kiện sai",
        "teacher_username": "teacher01",
        "teacher_name": "Giáo viên phản biện",
        "task": "Tìm dữ kiện sai trong câu trả lời AI.",
        "text": "Theo AI, Việt Nam hiện có hơn 120 triệu dân, nên mọi chính sách giáo dục trực tuyến phải ưu tiên mô hình lớp học đông trên 80 học sinh.",
        "error_type": "Dữ kiện sai",
        "suspicious_text": "hơn 120 triệu dân",
        "evidence": "Dân số Việt Nam chưa đạt 120 triệu; cần kiểm tra số liệu từ Tổng cục Thống kê hoặc nguồn quốc tế đáng tin cậy.",
        "rewrite": "Không nên suy luận chính sách từ một con số dân số chưa được kiểm chứng; cần dùng số liệu cập nhật và xem thêm điều kiện vùng miền, hạ tầng, giáo viên.",
        "active": True,
        "created_at": "demo",
    },
    {
        "id": "detective-station-b",
        "code": "B",
        "title": "Nguồn không tồn tại",
        "teacher_username": "teacher01",
        "teacher_name": "Giáo viên phản biện",
        "task": "Kiểm tra nguồn được AI viện dẫn.",
        "text": "AI khẳng định báo cáo 'Global Classroom Automation Index 2026' của UNESCO cho thấy 73% trường học đã thay giáo viên bằng trợ lý AI.",
        "error_type": "Nguồn không tồn tại",
        "suspicious_text": "Global Classroom Automation Index 2026",
        "evidence": "Tên báo cáo có dấu hiệu bịa hoặc cần xác minh trên kho tài liệu chính thức của UNESCO trước khi trích dẫn.",
        "rewrite": "Chỉ nên viết rằng một số tổ chức quốc tế đang thảo luận về AI trong giáo dục, và phải dẫn đúng tên báo cáo, năm phát hành, đường dẫn kiểm chứng.",
        "active": True,
        "created_at": "demo",
    },
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _normalize(value):
    text = unicodedata.normalize("NFD", str(value or "").lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def _content():
    data = load_json("teacher_content.json", {"argument_packages": [], "detective_cases": []})
    data.setdefault("argument_packages", [])
    data.setdefault("detective_cases", [])
    changed = False
    for package in DEFAULT_ARGUMENT_PACKAGES:
        if not any(item.get("id") == package["id"] for item in data["argument_packages"]):
            data["argument_packages"].append(deepcopy(package))
            changed = True
    for case in DEFAULT_DETECTIVE_CASES:
        if not any(item.get("id") == case["id"] for item in data["detective_cases"]):
            data["detective_cases"].append(deepcopy(case))
            changed = True
    if changed:
        save_json("teacher_content.json", data)
    return data


def _save(data):
    save_json("teacher_content.json", data)


def list_argument_packages(active_only=False):
    packages = list(reversed(_content()["argument_packages"]))
    return [item for item in packages if item.get("active")] if active_only else packages


def get_argument_package(package_id=None, active_only=False):
    packages = list_argument_packages(active_only=active_only)
    if package_id:
        selected = next((item for item in packages if item.get("id") == package_id), None)
        if selected:
            return selected
    return packages[0] if packages else None


def parse_argument_pieces(text):
    pieces = []
    valid_buckets = {bucket["key"] for bucket in ARGUMENT_BUCKETS}
    for index, line in enumerate(str(text or "").splitlines(), start=1):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 2 or not parts[0]:
            continue
        bucket = parts[1] if parts[1] in valid_buckets else "claim"
        pieces.append({"id": f"p{index}", "text": parts[0], "bucket": bucket})
    return pieces


def pieces_to_text(pieces):
    return "\n".join(f"{piece.get('text', '')}|{piece.get('bucket', 'claim')}" for piece in pieces or [])


def upsert_argument_package(form, teacher):
    data = _content()
    package_id = str(form.get("package_id") or "").strip()
    pieces = parse_argument_pieces(form.get("pieces"))
    title = str(form.get("title") or "").strip()
    question = str(form.get("question") or "").strip()
    source_text = str(form.get("source_text") or "").strip()
    if not title or not question or not source_text or len(pieces) < 2:
        raise ValueError("Gói bản đồ cần có tiêu đề, câu hỏi, văn bản nguồn và ít nhất 2 mảnh.")
    existing = next((item for item in data["argument_packages"] if item.get("id") == package_id), None) if package_id else None
    package = existing or {"id": str(uuid4()), "created_at": _now()}
    package.update(
        {
            "title": title,
            "teacher_username": (teacher or {}).get("username", ""),
            "teacher_name": (teacher or {}).get("name", "Giáo viên"),
            "question": question,
            "source_text": source_text,
            "buckets": deepcopy(ARGUMENT_BUCKETS),
            "pieces": pieces,
            "active": form.get("active", "on") == "on",
        }
    )
    if not existing:
        data["argument_packages"].append(package)
    _save(data)
    return package


def delete_argument_package(package_id):
    data = _content()
    data["argument_packages"] = [item for item in data["argument_packages"] if item.get("id") != package_id]
    _save(data)


def score_argument_package(package_id, placements):
    package = get_argument_package(package_id, active_only=True) or get_argument_package(active_only=True)
    placements = placements or {}
    pieces = package.get("pieces", []) if package else []
    total = len(pieces) or 1
    correct = 0
    details = []
    for piece in pieces:
        actual = placements.get(piece["id"])
        is_correct = actual == piece["bucket"]
        correct += 1 if is_correct else 0
        details.append({"piece_id": piece["id"], "expected": piece["bucket"], "actual": actual, "correct": is_correct})
    return {"score": round(correct / total * 100), "correct": correct, "total": len(pieces), "details": details}


def list_detective_cases(active_only=False):
    cases = sorted(_content()["detective_cases"], key=lambda item: str(item.get("code", "")))
    return [item for item in cases if item.get("active")] if active_only else cases


def get_detective_case(code="A", active_only=False):
    code = str(code or "A").upper()
    cases = list_detective_cases(active_only=active_only)
    for case in cases:
        if str(case.get("code", "")).upper() == code:
            return case
    return cases[0] if cases else None


def public_detective_case(case):
    return {"code": case["code"], "title": case["title"], "task": case["task"], "text": case["text"]}


def upsert_detective_case(form, teacher):
    data = _content()
    case_id = str(form.get("case_id") or "").strip()
    code = str(form.get("code") or "").strip().upper()[:2]
    fields = {
        "code": code,
        "title": str(form.get("title") or "").strip(),
        "task": str(form.get("task") or "").strip(),
        "text": str(form.get("text") or "").strip(),
        "error_type": str(form.get("error_type") or "").strip(),
        "suspicious_text": str(form.get("suspicious_text") or "").strip(),
        "evidence": str(form.get("evidence") or "").strip(),
        "rewrite": str(form.get("rewrite") or "").strip(),
    }
    if any(not value for value in fields.values()):
        raise ValueError("Vụ án cần đủ mã, tiêu đề, dữ kiện và đáp án.")
    existing = next((item for item in data["detective_cases"] if item.get("id") == case_id), None) if case_id else None
    case = existing or {"id": str(uuid4()), "created_at": _now()}
    case.update(
        {
            **fields,
            "teacher_username": (teacher or {}).get("username", ""),
            "teacher_name": (teacher or {}).get("name", "Giáo viên"),
            "active": form.get("active", "on") == "on",
        }
    )
    if not existing:
        data["detective_cases"].append(case)
    _save(data)
    return case


def delete_detective_case(case_id):
    data = _content()
    data["detective_cases"] = [item for item in data["detective_cases"] if item.get("id") != case_id]
    _save(data)


def score_detective_case(code, suspicious_text, error_type, explanation, evidence, rewrite):
    case = get_detective_case(code, active_only=True)
    suspicious = _normalize(str(suspicious_text or "").strip())
    expected_suspicious = _normalize(case.get("suspicious_text", ""))
    selected_type = _normalize(str(error_type or "").strip())
    expected_type = _normalize(case.get("error_type", ""))
    points = 0
    if expected_suspicious in suspicious or suspicious in expected_suspicious:
        points += 25
    if selected_type == expected_type:
        points += 25
    points += min(20, len(str(explanation or "").strip()) // 3)
    points += min(15, len(str(evidence or "").strip()) // 4)
    points += min(15, len(str(rewrite or "").strip()) // 5)
    return {"score": min(points, 100), "expected": case, "passed": points >= 60}
