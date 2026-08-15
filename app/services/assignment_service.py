from datetime import datetime, timezone
import re
from uuid import uuid4

from app.services.storage import load_json, save_json

DEFAULT_ASSIGNMENT_DATA = {
    "tasks": [
        {
            "id": "task-ai-learning-reflection",
            "title": "AI có làm học sinh lười suy nghĩ không?",
            "teacher_username": "teacher01",
            "teacher_name": "Giáo viên phản biện",
            "prompt": "Viết một đoạn lập luận ngắn trả lời câu hỏi: AI có làm học sinh lười suy nghĩ không?",
            "rubric": "Luận điểm rõ ràng: 25 điểm\nBằng chứng hoặc ví dụ: 25 điểm\nCó phản biện/điều kiện sử dụng: 25 điểm\nKết luận cân bằng: 25 điểm",
            "active": True,
            "created_at": "demo",
        }
    ],
    "attempts": [],
    "submissions": [],
    "consents": {},
}

DEMO_EXTRA_TASK = {
    "id": "task-source-checking-short-essay",
    "title": "Kiểm chứng nguồn trước khi tin AI",
    "teacher_username": "teacher01",
    "teacher_name": "Giáo viên phản biện",
    "prompt": "Viết 180-220 từ giải thích vì sao học sinh cần kiểm chứng ít nhất 2 nguồn trước khi dùng câu trả lời AI trong bài học.",
    "rubric": "Nêu luận điểm rõ: 20 điểm\nCó ví dụ lớp học cụ thể: 25 điểm\nChỉ ra rủi ro khi tin AI quá nhanh: 25 điểm\nĐề xuất cách kiểm chứng nguồn: 20 điểm\nDiễn đạt mạch lạc: 10 điểm",
    "active": True,
    "created_at": "demo-extra",
}

DEMO_EXTRA_ATTEMPT = {
    "id": "attempt-demo-source-checking-student01",
    "task_id": "task-source-checking-short-essay",
    "task_title": "Kiểm chứng nguồn trước khi tin AI",
    "student_username": "student01",
    "student_name": "Học sinh demo",
    "teacher_username": "teacher01",
    "teacher_name": "Giáo viên phản biện",
    "started_at": "2026-08-15T12:05:00+00:00",
    "submitted_at": "2026-08-15T12:23:20+00:00",
    "chat": [
        {
            "role": "student",
            "content": "Em nên kiểm chứng nguồn bằng cách nào cho nhanh?",
            "created_at": "2026-08-15T12:08:00+00:00",
        },
        {
            "role": "assistant",
            "content": "Em có thể đối chiếu với sách giáo khoa, trang chính thống và một nguồn độc lập. Nếu hai nguồn không khớp, hãy ghi rõ phần còn nghi ngờ.",
            "created_at": "2026-08-15T12:08:18+00:00",
        },
    ],
}

DEMO_EXTRA_SUBMISSION = {
    "id": "submission-demo-source-checking-student01",
    "task_id": "task-source-checking-short-essay",
    "task_title": "Kiểm chứng nguồn trước khi tin AI",
    "teacher_username": "teacher01",
    "teacher_name": "Giáo viên phản biện",
    "student_username": "student01",
    "student_name": "Học sinh demo",
    "prompt": DEMO_EXTRA_TASK["prompt"],
    "rubric": DEMO_EXTRA_TASK["rubric"],
    "answer": "Theo em, học sinh không nên tin ngay câu trả lời của AI vì AI có thể nói rất tự tin nhưng vẫn sai dữ kiện. Khi làm bài, em cần kiểm chứng ít nhất hai nguồn như sách giáo khoa, trang của cơ quan giáo dục hoặc tài liệu do giáo viên gợi ý. Ví dụ nếu AI nói một sự kiện lịch sử xảy ra vào một năm cụ thể, em sẽ kiểm tra lại trong sách và một trang đáng tin cậy trước khi đưa vào bài. Việc này giúp em tránh sao chép thông tin sai, đồng thời hiểu rõ hơn vì sao dữ kiện đó đúng. AI vẫn hữu ích để gợi ý hướng nghĩ, nhưng quyết định cuối cùng phải do học sinh tự kiểm tra và chịu trách nhiệm.",
    "ai_review": "Bài có luận điểm rõ và ví dụ phù hợp. Cần bổ sung thêm một câu về cách ghi lại nguồn đã kiểm chứng để giáo viên dễ theo dõi.",
    "ai_meta": {"model": "demo", "key_label": "demo"},
    "teacher_score": "",
    "teacher_review": "",
    "status": "pending_teacher_review",
    "attempt_id": DEMO_EXTRA_ATTEMPT["id"],
    "started_at": DEMO_EXTRA_ATTEMPT["started_at"],
    "submitted_at": DEMO_EXTRA_ATTEMPT["submitted_at"],
    "duration_seconds": 1100,
    "chat": DEMO_EXTRA_ATTEMPT["chat"],
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def clean_ai_text(value):
    text = str(value or "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"(?m)^\s{0,3}[-*]\s+", "", text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _data():
    data = load_json("assignments.json", DEFAULT_ASSIGNMENT_DATA)
    data.setdefault("tasks", [])
    data.setdefault("attempts", [])
    data.setdefault("submissions", [])
    data.setdefault("consents", {})
    changed = False
    if not any(task.get("id") == DEMO_EXTRA_TASK["id"] for task in data["tasks"]):
        data["tasks"].append(dict(DEMO_EXTRA_TASK))
        changed = True
    if not any(attempt.get("id") == DEMO_EXTRA_ATTEMPT["id"] for attempt in data["attempts"]):
        data["attempts"].append(dict(DEMO_EXTRA_ATTEMPT))
        changed = True
    if not any(submission.get("id") == DEMO_EXTRA_SUBMISSION["id"] for submission in data["submissions"]):
        data["submissions"].append(dict(DEMO_EXTRA_SUBMISSION))
        changed = True
    if changed:
        save_json("assignments.json", data)
    return data


def _save(data):
    save_json("assignments.json", data)


def list_tasks(active_only=False):
    tasks = list(_data().get("tasks", []))
    if active_only:
        tasks = [task for task in tasks if task.get("active")]
    return list(reversed(tasks))


def get_task(task_id=None, active_only=False):
    tasks = list_tasks(active_only=active_only)
    if task_id:
        selected = next((task for task in tasks if task.get("id") == task_id), None)
        if selected:
            return selected
    return tasks[0] if tasks else None


def upsert_task(form, teacher):
    data = _data()
    task_id = str(form.get("task_id") or "").strip()
    title = str(form.get("title") or "").strip()
    prompt = str(form.get("prompt") or "").strip()
    rubric = str(form.get("rubric") or "").strip()
    if not title or not prompt or not rubric:
        raise ValueError("Nhiệm vụ cần có tiêu đề, đề bài và rubric.")

    existing = next((task for task in data["tasks"] if task.get("id") == task_id), None) if task_id else None
    task = existing or {"id": str(uuid4()), "created_at": _now()}
    task.update(
        {
            "title": title,
            "teacher_username": (teacher or {}).get("username", ""),
            "teacher_name": (teacher or {}).get("name", "Giáo viên"),
            "prompt": prompt,
            "rubric": rubric,
            "active": form.get("active", "on") == "on",
        }
    )
    if not existing:
        data["tasks"].append(task)
    _save(data)
    return task


def delete_task(task_id):
    data = _data()
    before = len(data["tasks"])
    data["tasks"] = [task for task in data["tasks"] if task.get("id") != task_id]
    if len(data["tasks"]) == before:
        raise ValueError("Không tìm thấy nhiệm vụ.")
    _save(data)


def has_consent(username, task_id):
    if not username or not task_id:
        return False
    return bool(_data().get("consents", {}).get(username, {}).get(task_id))


def accept_consent(username, task_id):
    data = _data()
    data.setdefault("consents", {}).setdefault(username, {})[task_id] = {
        "accepted": True,
        "accepted_at": _now(),
    }
    _save(data)


def start_attempt(student, task):
    data = _data()
    open_attempt = next(
        (
            attempt
            for attempt in reversed(data["attempts"])
            if attempt.get("student_username") == student.get("username")
            and attempt.get("task_id") == task.get("id")
            and not attempt.get("submitted_at")
        ),
        None,
    )
    if open_attempt:
        return open_attempt

    attempt = {
        "id": str(uuid4()),
        "task_id": task["id"],
        "task_title": task["title"],
        "student_username": student.get("username", ""),
        "student_name": student.get("name", student.get("username", "")),
        "teacher_username": task.get("teacher_username", ""),
        "teacher_name": task.get("teacher_name", ""),
        "started_at": _now(),
        "submitted_at": "",
        "chat": [],
    }
    data["attempts"].append(attempt)
    _save(data)
    return attempt


def append_chat(attempt_id, role, content):
    data = _data()
    attempt = next((item for item in data["attempts"] if item.get("id") == attempt_id), None)
    if not attempt:
        raise ValueError("Không tìm thấy phiên làm bài.")
    message = {
        "role": str(role or "user"),
        "content": str(content or "").strip(),
        "created_at": _now(),
    }
    attempt.setdefault("chat", []).append(message)
    _save(data)
    return attempt, message


def save_submission(student, task, attempt_id, answer, ai_review, ai_meta):
    data = _data()
    now = _now()
    attempt = next((item for item in data["attempts"] if item.get("id") == attempt_id), None)
    if not attempt:
        attempt = start_attempt(student, task)
        attempt_id = attempt["id"]

    attempt["submitted_at"] = now
    duration_seconds = _duration_seconds(attempt.get("started_at"), now)
    submission = {
        "id": str(uuid4()),
        "task_id": task["id"],
        "task_title": task["title"],
        "teacher_username": task.get("teacher_username", ""),
        "teacher_name": task.get("teacher_name", ""),
        "student_username": student.get("username", ""),
        "student_name": student.get("name", student.get("username", "")),
        "prompt": task["prompt"],
        "rubric": task["rubric"],
        "answer": str(answer or "").strip(),
        "ai_review": str(ai_review or "").strip(),
        "ai_meta": ai_meta or {},
        "teacher_score": "",
        "teacher_review": "",
        "status": "pending_teacher_review",
        "attempt_id": attempt_id,
        "started_at": attempt.get("started_at", now),
        "submitted_at": now,
        "duration_seconds": duration_seconds,
        "chat": attempt.get("chat", []),
    }
    data["submissions"].append(submission)
    _save(data)
    return submission


def list_submissions(limit=40):
    return list(reversed(_data().get("submissions", [])[-limit:]))


def update_teacher_review(submission_id, score, review):
    data = _data()
    submission = next((item for item in data["submissions"] if item.get("id") == submission_id), None)
    if not submission:
        raise ValueError("Không tìm thấy bài nộp.")
    submission["teacher_score"] = str(score or "").strip()
    submission["teacher_review"] = str(review or "").strip()
    submission["status"] = "teacher_reviewed"
    submission["reviewed_at"] = _now()
    _save(data)
    return submission


def _duration_seconds(started_at, submitted_at):
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(submitted_at)
    except (TypeError, ValueError):
        return 0
    return max(0, int((end - start).total_seconds()))


def format_duration(seconds):
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0
    minutes, rest = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}g {minutes}p"
    return f"{minutes}p {rest}s"


def build_assignment_review_prompt(task, answer, chat_log, duration_label):
    transcript = "\n".join(
        f"{message.get('role', 'user')}: {message.get('content', '')}"
        for message in (chat_log or [])[-20:]
    )
    return f"""
Bạn là trợ lý chấm sơ bộ cho giáo viên. Chỉ nhận xét, không chốt điểm cuối cùng.

Đề bài:
{task.get("prompt", "")}

Rubric giáo viên đưa:
{task.get("rubric", "")}

Bài làm học sinh:
{answer}

Thời gian làm bài: {duration_label}

Cuộc trò chuyện học sinh hỏi AI:
{transcript or "Không có trao đổi với AI."}

Hãy trả lời ngắn gọn theo 4 mục:
1. Điểm mạnh
2. Điểm cần bổ sung
3. Dấu hiệu học sinh tự suy nghĩ hay phụ thuộc AI
4. Gợi ý để giáo viên chấm cuối
""".strip()


def build_assignment_chat_prompt(task, messages):
    transcript = "\n".join(
        f"{message.get('role', 'user')}: {message.get('content', '')}"
        for message in (messages or [])[-12:]
    )
    return f"""
Bạn là trợ lý học tập trong lúc học sinh làm nhiệm vụ. Không viết hộ toàn bộ bài.
Chỉ gợi mở, đặt câu hỏi, nhắc rubric và giúp học sinh tự triển khai.

Đề bài:
{task.get("prompt", "")}

Rubric:
{task.get("rubric", "")}

Hội thoại:
{transcript}

Trả lời ngắn, thân thiện, tối đa 5 câu. Không dùng markdown, không dùng dấu **, không tạo tiêu đề in đậm.
""".strip()


def fallback_assignment_chat(task, question):
    return (
        "Em thử bám vào rubric của giáo viên: nêu luận điểm chính, thêm một ví dụ, "
        "rồi tự hỏi phần nào có thể bị phản biện. Với câu em vừa hỏi, hãy viết trước "
        "một ý nháp ngắn, AI chỉ giúp em soi lại chỗ còn thiếu."
    )


def fallback_assignment_review(task, answer, chat_log, duration_label):
    chat_count = len(chat_log or [])
    answer_len = len(str(answer or "").split())
    return (
        f"AI nhận xét sơ bộ: bài có khoảng {answer_len} từ, thời gian làm {duration_label}, "
        f"có {chat_count} lượt trao đổi với AI. Giáo viên nên đối chiếu rubric để xem luận điểm, "
        "bằng chứng, phản biện và kết luận đã đủ chưa trước khi chốt điểm."
    )
