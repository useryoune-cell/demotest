from datetime import datetime, timezone
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


def _now():
    return datetime.now(timezone.utc).isoformat()


def _data():
    data = load_json("assignments.json", DEFAULT_ASSIGNMENT_DATA)
    data.setdefault("tasks", [])
    data.setdefault("attempts", [])
    data.setdefault("submissions", [])
    data.setdefault("consents", {})
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

Trả lời ngắn, thân thiện, tối đa 5 câu.
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
