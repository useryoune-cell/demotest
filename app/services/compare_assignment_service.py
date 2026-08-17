from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json

DEFAULT_COMPARE_DATA = {
    "packages": [
        {
            "id": "compare-ai-homework",
            "title": "AI trong bài tập về nhà",
            "teacher_username": "teacher01",
            "teacher_name": "Giáo viên phản biện",
            "question": "Có nên cho phép học sinh sử dụng AI tạo sinh trong tất cả bài tập về nhà?",
            "answers": [
                {
                    "label": "A",
                    "text": "Có thể cho phép học sinh dùng AI nếu giáo viên đặt quy định rõ. AI giúp tìm ý, giải thích và luyện tập, nhưng học sinh không nên sao chép nguyên văn.",
                },
                {
                    "label": "B",
                    "text": "Nên cho dùng AI trong mọi bài tập vì các nghiên cứu đã chứng minh AI luôn làm học sinh tư duy phản biện tốt hơn và không gây phụ thuộc.",
                },
                {
                    "label": "C",
                    "text": "Không nên cho dùng AI vì học sinh có thể sao chép, giáo viên khó biết bài làm thật, dữ liệu cá nhân có thể bị đưa vào công cụ. Vì vậy, AI nên bị cấm trong bài tập về nhà.",
                },
            ],
            "best": "A",
            "active": True,
            "created_at": "demo",
        }
    ],
    "submissions": [],
}

DEMO_EXTRA_PACKAGE = {
    "id": "compare-climate-ai-source",
    "title": "Nhận diện câu trả lời AI thiếu nguồn",
    "teacher_username": "teacher01",
    "teacher_name": "Giáo viên phản biện",
    "question": "Khi hỏi AI về biến đổi khí hậu ở Việt Nam, câu trả lời nào đáng dùng nhất cho bài thuyết trình lớp 8?",
    "answers": [
        {
            "label": "A",
            "text": "Biến đổi khí hậu làm thời tiết cực đoan hơn. Học sinh nên kiểm chứng bằng báo cáo của cơ quan khí tượng hoặc tài liệu giáo viên cung cấp trước khi dùng số liệu.",
        },
        {
            "label": "B",
            "text": "Biến đổi khí hậu chắc chắn sẽ làm mọi thành phố ven biển biến mất trong vài năm tới, vì nhiều người trên mạng đã nói như vậy.",
        },
        {
            "label": "C",
            "text": "Khí hậu thay đổi là chuyện bình thường nên không cần quan tâm đến nguồn hay dữ liệu khi trình bày.",
        },
    ],
    "best": "A",
    "active": True,
    "created_at": "demo-extra",
}

DEMO_EXTRA_SUBMISSION = {
    "id": "compare-submission-demo-student01-source",
    "student_username": "student01",
    "student_name": "Học sinh demo",
    "package_id": "compare-climate-ai-source",
    "package_title": "Nhận diện câu trả lời AI thiếu nguồn",
    "teacher_username": "teacher01",
    "teacher_name": "Giáo viên phản biện",
    "question": DEMO_EXTRA_PACKAGE["question"],
    "selected": "A",
    "criteria": "Em chọn A vì câu này không phóng đại, có nhắc đến kiểm chứng bằng nguồn đáng tin và phù hợp để đưa vào bài thuyết trình.",
    "synthesis": "Câu trả lời tốt cần vừa nêu ý chính vừa chỉ ra cách kiểm tra số liệu trước khi dùng.",
    "score": 88,
    "correct": True,
    "created_at": "2026-08-15T12:30:00+00:00",
}


def _data():
    data = load_json("compare_assignments.json", DEFAULT_COMPARE_DATA)
    data.setdefault("packages", [])
    data.setdefault("submissions", [])
    for submission in data["submissions"]:
        submission.setdefault("teacher_score", "")
        submission.setdefault("teacher_review", "")
        submission.setdefault("status", "pending_teacher_review")
    changed = False
    if not any(package.get("id") == DEMO_EXTRA_PACKAGE["id"] for package in data["packages"]):
        data["packages"].append(dict(DEMO_EXTRA_PACKAGE))
        changed = True
    if not any(submission.get("id") == DEMO_EXTRA_SUBMISSION["id"] for submission in data["submissions"]):
        data["submissions"].append(dict(DEMO_EXTRA_SUBMISSION))
        changed = True
    if changed:
        save_json("compare_assignments.json", data)
    return data


def _save(data):
    save_json("compare_assignments.json", data)


def _clean_answer(value):
    return str(value or "").strip()


def _normalize_package(package):
    answers = package.get("answers") or []
    normalized_answers = []
    for index, label in enumerate(("A", "B", "C")):
        item = answers[index] if index < len(answers) else {}
        normalized_answers.append({"label": label, "text": _clean_answer(item.get("text"))})
    package["answers"] = normalized_answers
    package["best"] = str(package.get("best") or "A").strip().upper()
    if package["best"] not in {"A", "B", "C"}:
        package["best"] = "A"
    package["active"] = bool(package.get("active", True))
    return package


def list_compare_packages(active_only=False):
    packages = [_normalize_package(dict(package)) for package in _data().get("packages", [])]
    if active_only:
        packages = [package for package in packages if package.get("active")]
    return list(reversed(packages))


def get_compare_package(package_id=None):
    packages = list_compare_packages(active_only=True)
    if package_id:
        selected = next((package for package in packages if package["id"] == package_id), None)
        if selected:
            return selected
    return packages[0] if packages else None


def upsert_compare_package(form, teacher):
    data = _data()
    package_id = str(form.get("package_id") or "").strip()
    title = str(form.get("title") or "").strip()
    question = str(form.get("question") or "").strip()
    answers = [
        {"label": "A", "text": _clean_answer(form.get("answer_a"))},
        {"label": "B", "text": _clean_answer(form.get("answer_b"))},
        {"label": "C", "text": _clean_answer(form.get("answer_c"))},
    ]
    if not title or not question or any(not answer["text"] for answer in answers):
        raise ValueError("Gói bài cần có tiêu đề, câu hỏi và đủ 3 câu trả lời AI.")

    existing = None
    if package_id:
        existing = next((item for item in data["packages"] if item["id"] == package_id), None)

    package = existing or {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    package.update(
        {
            "title": title,
            "teacher_username": (teacher or {}).get("username", ""),
            "teacher_name": (teacher or {}).get("name", "Giáo viên"),
            "question": question,
            "answers": answers,
            "best": str(form.get("best") or "A").strip().upper(),
            "active": form.get("active", "on") == "on",
        }
    )
    _normalize_package(package)

    if not existing:
        data["packages"].append(package)
    _save(data)
    return package


def delete_compare_package(package_id):
    data = _data()
    before = len(data["packages"])
    data["packages"] = [package for package in data["packages"] if package.get("id") != package_id]
    if len(data["packages"]) == before:
        raise ValueError("Không tìm thấy gói bài.")
    _save(data)


def save_compare_submission(student, package, selected, criteria, synthesis, score, correct):
    if not student or not package:
        return None
    data = _data()
    entry = {
        "id": str(uuid4()),
        "student_username": student.get("username", ""),
        "student_name": student.get("name", student.get("username", "")),
        "package_id": package["id"],
        "package_title": package["title"],
        "teacher_username": package.get("teacher_username", ""),
        "teacher_name": package.get("teacher_name", ""),
        "question": package["question"],
        "selected": str(selected or "").strip().upper(),
        "criteria": str(criteria or "").strip(),
        "synthesis": str(synthesis or "").strip(),
        "score": score,
        "correct": bool(correct),
        "teacher_score": "",
        "teacher_review": "",
        "status": "pending_teacher_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data["submissions"].append(entry)
    _save(data)
    return entry


def list_compare_submissions(limit=30):
    submissions = _data().get("submissions", [])
    return list(reversed(submissions[-limit:]))


def update_compare_submission_review(submission_id, score, review):
    data = _data()
    submission = next((item for item in data["submissions"] if item.get("id") == submission_id), None)
    if not submission:
        raise ValueError("Không tìm thấy bài so sánh.")
    submission["teacher_score"] = str(score or "").strip()
    submission["teacher_review"] = str(review or "").strip()
    submission["status"] = "teacher_reviewed"
    submission["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    _save(data)
    return submission
