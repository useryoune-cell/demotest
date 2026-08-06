import json
from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json


REFLECTION_QUESTIONS = [
    "Ban đầu em nghĩ gì?",
    "AI đưa ra điều gì khác với suy nghĩ của em?",
    "Em tin phần nào trong phản hồi của AI?",
    "Em nghi ngờ phần nào?",
    "Em đã hoặc sẽ kiểm chứng bằng cách nào?",
    "Em có thay đổi quan điểm không? Vì sao?",
    "Nếu làm lại, em sẽ đặt câu hỏi khác như thế nào?",
]

REFLECTION_DRAFT_SCHEMA = {
    "summary": "Chưa có phiên học nào được chuyển sang nhật ký.",
    "ai_review": "Khi hoàn thành một hoạt động, AI sẽ tóm tắt điểm mạnh và điểm cần kiểm chứng ở đây.",
    "student_takeaway": "",
    "source_module": "manual",
}

DEFAULT_REFLECTION_DATA = {}


def _data():
    return load_json("reflections.json", DEFAULT_REFLECTION_DATA)


def _save(data):
    save_json("reflections.json", data)


def save_reflection(payload, username):
    data = _data()
    answers = payload.get("answers") or {}
    cleaned_answers = {
        str(index): str(value).strip()
        for index, value in answers.items()
        if str(value).strip()
    }
    entry = {
        "id": str(uuid4()),
        "student_username": username,
        "module": str(payload.get("module") or "unknown"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "answers": cleaned_answers,
        "context": payload.get("context") or {},
    }
    data.setdefault(username, []).append(entry)
    _save(data)
    return entry


def build_reflection_draft_prompt(messages, board, mode):
    history = "\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '')}" for item in (messages or [])[-14:]
    )
    board_text = json.dumps(board or {}, ensure_ascii=False)
    return f"""
Bạn là chuyên gia phản biện đang giúp học sinh THPT Việt Nam tạo nhật ký phản tư sau phiên học.
Không chấm điểm. Không viết dài.

Phiên chatbot: {mode}

Lịch sử hội thoại:
{history}

Bảng tư duy:
{board_text}

Hãy trả về JSON hợp lệ, không markdown:
{{
  "summary": "Tóm tắt 2-3 câu về nội dung học sinh vừa trao đổi.",
  "ai_review": "Nhận xét sơ bộ 3-4 câu: điểm mạnh, điểm cần kiểm chứng, kỹ năng nên rèn.",
  "student_takeaway": ""
}}
""".strip()


def parse_reflection_draft(raw_text):
    text = (raw_text or "").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(text[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("Reflection draft is not a JSON object.")

    return {
        "summary": str(data.get("summary") or REFLECTION_DRAFT_SCHEMA["summary"]).strip()[:1200],
        "ai_review": str(data.get("ai_review") or REFLECTION_DRAFT_SCHEMA["ai_review"]).strip()[:1600],
        "student_takeaway": str(data.get("student_takeaway") or "").strip()[:1000],
        "source_module": "chatbot-socratic",
    }


def fallback_reflection_draft(messages, board, mode):
    user_messages = [
        str(item.get("content", "")).strip()
        for item in (messages or [])
        if item.get("role") == "user" and str(item.get("content", "")).strip()
    ]
    latest = user_messages[-1] if user_messages else ""
    claims = (board or {}).get("claims") or []
    evidence = (board or {}).get("evidence") or []
    unclear = (board or {}).get("unclear") or []

    summary_parts = []
    if latest:
        summary_parts.append(f"Học sinh vừa trao đổi về: {latest[:220]}")
    if claims:
        summary_parts.append(f"Nhận định nổi bật: {str(claims[-1])[:220]}")
    if evidence:
        summary_parts.append(f"Bằng chứng đã nêu: {str(evidence[-1])[:220]}")

    review_parts = [
        "Phiên học đã có dữ liệu để tiếp tục phản tư.",
        "Điểm nên làm tiếp là kiểm tra lại căn cứ, làm rõ giả định và thử nhìn từ quan điểm ngược lại.",
    ]
    if unclear:
        review_parts.append(f"Điều còn chưa rõ: {str(unclear[-1])[:220]}")
    if mode == "easy":
        review_parts.append("Nên viết kết luận ngắn theo mẫu: Em nghĩ..., vì..., em cần kiểm chứng thêm...")
    else:
        review_parts.append("Nên thử tự phản biện lập luận của mình bằng một phản ví dụ cụ thể.")

    return {
        "summary": " ".join(summary_parts) or REFLECTION_DRAFT_SCHEMA["summary"],
        "ai_review": " ".join(review_parts),
        "student_takeaway": "",
        "source_module": "chatbot-socratic",
    }


def recent_reflections(username, limit=8):
    entries = _data().get(username, [])
    return list(reversed(entries[-limit:]))


def transfer_reflections(source_username, target_username):
    if not source_username or not target_username or source_username == target_username:
        return
    data = _data()
    entries = data.pop(source_username, [])
    for entry in entries:
        entry["student_username"] = target_username
    if entries:
        data.setdefault(target_username, []).extend(entries)
        _save(data)
