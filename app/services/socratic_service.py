import json


SOCRATIC_STAGES = [
    {"key": "PROBE", "label": "Hỏi đã biết gì"},
    {"key": "CLAIM", "label": "Nhận định ban đầu"},
    {"key": "EVIDENCE", "label": "Căn cứ"},
    {"key": "COUNTER", "label": "Phản ví dụ"},
    {"key": "REVISE", "label": "Điều chỉnh"},
    {"key": "SYNTHESIZE", "label": "Tổng hợp"},
]

BOARD_KEYS = {
    "claims": "Nhận định",
    "evidence": "Bằng chứng",
    "unclear": "Điều chưa rõ",
    "counterpoints": "Phản biện",
    "revisions": "Điều chỉnh",
}


SOCRATIC_MODES = {
    "easy": {
        "label": "Dễ tiếp cận",
        "system": """
Chế độ Dễ tiếp cận:
- Dành cho học sinh mới bắt đầu hoặc chưa biết trả lời.
- Được phép gợi ý hướng làm bằng 2-3 gạch đầu dòng ngắn.
- Được phép đưa khung câu trả lời, ví dụ: "Em có thể bắt đầu bằng: Theo em..., vì..."
- Không viết nguyên đáp án hoàn chỉnh thay học sinh.
- Sau phần gợi ý, hãy hỏi 1 câu rất cụ thể để học sinh viết tiếp.
""".strip(),
    },
    "advanced": {
        "label": "Nâng cao",
        "system": """
Chế độ Nâng cao:
- Dành cho học sinh đã có nền tảng tốt.
- Không đưa đáp án hoàn chỉnh ngay.
- Ưu tiên chất vấn, yêu cầu bằng chứng, phản ví dụ và giúp học sinh tự điều chỉnh lập luận.
- Chỉ hỏi 1-2 câu trọng tâm ở mỗi lượt, trừ giai đoạn SYNTHESIZE.
""".strip(),
    },
}


def normalize_socratic_mode(mode):
    mode = str(mode or "easy").strip().lower()
    return mode if mode in SOCRATIC_MODES else "easy"


def build_socratic_prompt(messages, stage_index, board, mode="easy"):
    safe_stage_index = min(max(int(stage_index or 0), 0), len(SOCRATIC_STAGES) - 1)
    stage = SOCRATIC_STAGES[safe_stage_index]
    safe_mode = normalize_socratic_mode(mode)
    mode_config = SOCRATIC_MODES[safe_mode]
    history = "\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '')}" for item in messages[-10:]
    )
    board_text = json.dumps(board or {}, ensure_ascii=False)

    return f"""
Bạn là Chatbot Socratic trong AI Critical Thinking Lab cho học sinh THPT Việt Nam.
Mục tiêu: giúp học sinh tự hình thành lập luận, không làm bài thay học sinh.
Phiên bản đang dùng: {mode_config["label"]}.
{mode_config["system"]}

Giai đoạn hiện tại: {safe_stage_index} - {stage["key"]}: {stage["label"]}.
Chuỗi giai đoạn: PROBE -> CLAIM -> EVIDENCE -> COUNTER -> REVISE -> SYNTHESIZE.

Lịch sử hội thoại gần nhất:
{history}

Bảng tư duy hiện tại dạng JSON:
{board_text}

Yêu cầu phản hồi:
1. Trả lời ngắn, thân thiện, bằng tiếng Việt.
2. Bám đúng phiên bản đang dùng.
3. Nếu học sinh chưa nêu nhận định, hãy kéo về CLAIM.
4. Nếu học sinh nêu nhận định nhưng thiếu căn cứ, hãy kéo về EVIDENCE.
5. Nếu đã có căn cứ, hãy đưa phản ví dụ hoặc điểm chưa nhất quán ở COUNTER.
6. Nếu học sinh đã sửa lập luận, hãy chuyển REVISE hoặc SYNTHESIZE.
7. Tự gắn nhãn các mảnh tư duy mới từ câu trả lời của học sinh.

Chỉ trả về JSON hợp lệ, không markdown, theo schema:
{{
  "ai_message": "tin nhắn của AI",
  "stage_index": 0,
  "labels": [
    {{"type": "Nhận định", "text": "mảnh tư duy ngắn"}}
  ],
  "board_updates": {{
    "claims": [],
    "evidence": [],
    "unclear": [],
    "counterpoints": [],
    "revisions": []
  }}
}}
""".strip()


def parse_socratic_response(raw_text, current_stage_index):
    data = _load_json_object(raw_text)
    if not isinstance(data, dict):
        raise ValueError("Socratic response is not a JSON object.")

    ai_message = str(data.get("ai_message", "")).strip()
    if not ai_message:
        ai_message = "Em thử nói rõ hơn nhận định của mình và bằng chứng em đang dựa vào nhé."

    stage_index = data.get("stage_index", current_stage_index)
    try:
        stage_index = int(stage_index)
    except (TypeError, ValueError):
        stage_index = current_stage_index
    stage_index = min(max(stage_index, 0), len(SOCRATIC_STAGES) - 1)

    labels = data.get("labels") or []
    if not isinstance(labels, list):
        labels = []
    labels = [
        {
            "type": str(item.get("type", "Điều chưa rõ")).strip()[:40],
            "text": str(item.get("text", "")).strip()[:240],
        }
        for item in labels
        if isinstance(item, dict) and str(item.get("text", "")).strip()
    ][:5]

    updates = data.get("board_updates") or {}
    if not isinstance(updates, dict):
        updates = {}

    clean_updates = {}
    for key in BOARD_KEYS:
        values = updates.get(key) or []
        if not isinstance(values, list):
            values = [values]
        clean_updates[key] = [str(value).strip()[:240] for value in values if str(value).strip()][:4]

    return {
        "ai_message": ai_message,
        "stage_index": stage_index,
        "stage": SOCRATIC_STAGES[stage_index],
        "labels": labels,
        "board_updates": clean_updates,
    }


def fallback_socratic_response(current_stage_index):
    stage_index = min(current_stage_index + 1, len(SOCRATIC_STAGES) - 1)
    return {
        "ai_message": "Em hãy nêu rõ nhận định chính và một bằng chứng cụ thể để mình cùng kiểm tra độ vững của lập luận.",
        "stage_index": stage_index,
        "stage": SOCRATIC_STAGES[stage_index],
        "labels": [],
        "board_updates": {key: [] for key in BOARD_KEYS},
    }


def _load_json_object(raw_text):
    text = (raw_text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])
