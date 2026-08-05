HUMAN_FIRST_QUESTIONS = [
    {
        "id": "august-revolution",
        "subject": "Lịch sử",
        "question": "Vì sao Cách mạng tháng Tám năm 1945 thành công?",
        "hint": "Hãy nêu nhận định chính, ít nhất một bằng chứng lịch sử và điều em còn chưa chắc.",
    },
    {
        "id": "ai-homework",
        "subject": "Giáo dục công dân",
        "question": "Có nên cho phép học sinh dùng AI tạo sinh trong tất cả bài tập về nhà không?",
        "hint": "Hãy nêu lập trường, lý do, bằng chứng hoặc ví dụ, và một ngoại lệ có thể xảy ra.",
    },
    {
        "id": "climate-policy",
        "subject": "Địa lí",
        "question": "Một thành phố nên ưu tiên xe buýt điện hay mở rộng đường cho xe cá nhân?",
        "hint": "Hãy cân nhắc chi phí, môi trường, công bằng tiếp cận và dữ liệu cần kiểm chứng.",
    },
]


def get_human_first_question(question_id=None):
    if question_id:
        for question in HUMAN_FIRST_QUESTIONS:
            if question["id"] == question_id:
                return question
    return HUMAN_FIRST_QUESTIONS[0]


def build_ai_after_human_prompt(question, student_answer, confidence):
    return f"""
Bạn là AI trong mô-đun "Con người trước - AI sau" của AI Critical Thinking Lab.
Học sinh đã tự trả lời trước khi xem AI. Nhiệm vụ của bạn không phải áp đảo câu trả lời của học sinh,
mà đưa một câu trả lời mẫu có căn cứ, chỉ ra điểm cần kiểm chứng và giữ chỗ cho phán đoán độc lập.

Câu hỏi:
{question["question"]}

Câu trả lời ban đầu của học sinh:
{student_answer}

Mức độ chắc chắn học sinh tự chọn: {confidence}/100.

Hãy trả lời bằng tiếng Việt, gồm 4 phần ngắn:
1. Câu trả lời AI đề xuất.
2. Điểm câu trả lời của học sinh đang làm tốt.
3. Điểm cần kiểm chứng hoặc còn thiếu.
4. Một câu hỏi phản tư trước khi học sinh quyết định giữ hay đổi câu trả lời.
""".strip()
