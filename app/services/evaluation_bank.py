TRUST_ITEMS = [
    {
        "id": "trust-august-1945",
        "question": "Vì sao Cách mạng tháng Tám năm 1945 thành công?",
        "ai_answer": "Cách mạng tháng Tám thành công chủ yếu vì Nhật đầu hàng Đồng minh, tạo khoảng trống quyền lực. Ngoài ra, lực lượng cách mạng đã có quá trình chuẩn bị lâu dài và biết chớp thời cơ.",
        "evidence": "Nhật tuyên bố đầu hàng Đồng minh ngày 15/8/1945; trước đó Việt Minh đã xây dựng lực lượng chính trị, căn cứ và tổ chức quần chúng qua nhiều năm.",
        "ground_truth": 86,
        "explanation": "Câu trả lời tương đối đáng tin vì nêu đúng thời cơ khách quan và chuẩn bị chủ quan, nhưng còn thiếu chiều sâu về tổ chức, lãnh đạo và phong trào quần chúng.",
    },
    {
        "id": "trust-fake-source",
        "question": "AI có thể thay thế hoàn toàn giáo viên trong lớp học không?",
        "ai_answer": "Theo báo cáo UNESCO 2024 'AI Teachers Replace Schools', AI có thể thay thế giáo viên trong hầu hết lớp học phổ thông nếu được huấn luyện đủ dữ liệu.",
        "evidence": "Không có báo cáo UNESCO phổ biến nào mang tên như vậy. Khuyến nghị của UNESCO thường nhấn mạnh vai trò chủ động, giám sát và trách nhiệm của con người trong giáo dục có AI.",
        "ground_truth": 18,
        "explanation": "Câu trả lời đáng nghi vì viện dẫn nguồn có dấu hiệu không tồn tại và khái quát quá mức về việc thay thế giáo viên.",
    },
    {
        "id": "trust-electric-bus",
        "question": "Xe buýt điện luôn tốt hơn xe buýt diesel trong mọi điều kiện phải không?",
        "ai_answer": "Xe buýt điện thường giảm phát thải tại đô thị và tiếng ồn, nhưng lợi ích thực tế phụ thuộc nguồn điện, chi phí pin, hạ tầng sạc và vòng đời phương tiện.",
        "evidence": "Đánh giá chính sách giao thông cần xét phát thải vòng đời, nguồn điện, chi phí vận hành, tuổi thọ pin và năng lực hạ tầng.",
        "ground_truth": 91,
        "explanation": "Câu trả lời đáng tin vì tránh tuyệt đối hóa và nêu các điều kiện cần kiểm chứng.",
    },
]

COMPARE_ITEMS = [
    {
        "id": "compare-ai-homework",
        "question": "Có nên cho phép học sinh sử dụng AI tạo sinh trong tất cả bài tập về nhà?",
        "answers": [
            {
                "label": "A",
                "type": "Chính xác nhưng thiếu chiều sâu",
                "text": "Có thể cho phép học sinh dùng AI nếu giáo viên đặt quy định rõ. AI giúp tìm ý, giải thích và luyện tập, nhưng học sinh không nên sao chép nguyên văn.",
                "strength": "Nêu được điều kiện sử dụng và rủi ro sao chép.",
                "weakness": "Thiếu ví dụ cụ thể và chưa bàn về kiểm chứng, quyền riêng tư, đánh giá.",
            },
            {
                "label": "B",
                "type": "Thuyết phục nhưng có lỗi",
                "text": "Nên cho dùng AI trong mọi bài tập vì các nghiên cứu đã chứng minh AI luôn làm học sinh tư duy phản biện tốt hơn và không gây phụ thuộc.",
                "strength": "Lập trường rõ và giọng văn thuyết phục.",
                "weakness": "Khái quát hóa quá mức, dùng từ 'luôn', bỏ qua nguy cơ phụ thuộc và học vẹt.",
            },
            {
                "label": "C",
                "type": "Nhiều bằng chứng nhưng thiên lệch",
                "text": "Không nên cho dùng AI vì nhiều học sinh có thể sao chép, giáo viên khó biết bài làm thật, dữ liệu cá nhân có thể bị đưa vào công cụ. Vì vậy, AI nên bị cấm trong bài tập về nhà.",
                "strength": "Nêu nhiều rủi ro thực tế.",
                "weakness": "Thiên lệch về phía cấm hoàn toàn, chưa xét cách dùng có kiểm soát.",
            },
        ],
        "best": "A",
        "suggested_synthesis": "Có thể cho phép học sinh dùng AI trong bài tập về nhà nhưng cần quy định rõ mục đích, yêu cầu ghi cách dùng, kiểm chứng nguồn, nộp phần tự suy nghĩ trước và có dạng bài đánh giá năng lực lập luận riêng.",
    }
]

ERROR_ITEMS = [
    {
        "id": "error-level-1",
        "level": 1,
        "level_name": "Dễ nhận biết",
        "question": "Thủ đô của Việt Nam là gì?",
        "ai_answer": "Thủ đô của Việt Nam là Thành phố Hồ Chí Minh, trung tâm chính trị lớn nhất cả nước.",
        "error_type": "Dữ kiện sai",
        "suspicious_text": "Thành phố Hồ Chí Minh",
        "corrected_answer": "Thủ đô của Việt Nam là Hà Nội. Thành phố Hồ Chí Minh là trung tâm kinh tế lớn, không phải thủ đô.",
        "evidence": "Các văn bản hành chính và thông tin chính thức của Việt Nam xác định Hà Nội là thủ đô.",
    },
    {
        "id": "error-level-2",
        "level": 2,
        "level_name": "Pha trộn đúng - sai",
        "question": "Vì sao Cách mạng tháng Tám năm 1945 thành công?",
        "ai_answer": "Cách mạng tháng Tám thành công vì Nhật đầu hàng Đồng minh và vì Việt Minh đã chuẩn bị lực lượng. Tuy nhiên, phong trào này chủ yếu diễn ra sau năm 1945 nên chưa có quá trình chuẩn bị trước đó đáng kể.",
        "error_type": "Đúng nhưng sai bối cảnh",
        "suspicious_text": "chủ yếu diễn ra sau năm 1945",
        "corrected_answer": "Cần nêu cả thời cơ Nhật đầu hàng và quá trình chuẩn bị lực lượng, tổ chức, căn cứ, phong trào quần chúng trước năm 1945.",
        "evidence": "Việt Minh thành lập năm 1941; phong trào và căn cứ cách mạng đã được chuẩn bị trước Tổng khởi nghĩa.",
    },
    {
        "id": "error-level-3",
        "level": 3,
        "level_name": "Lỗi lập luận",
        "question": "Nếu một học sinh dùng AI và được điểm cao, có thể kết luận AI luôn làm học sinh học tốt hơn không?",
        "ai_answer": "Có. Nếu một học sinh dùng AI và được điểm cao, điều đó chứng minh AI luôn cải thiện kết quả học tập của học sinh.",
        "error_type": "Khái quát hóa quá mức",
        "suspicious_text": "chứng minh AI luôn cải thiện",
        "corrected_answer": "Một trường hợp điểm cao không đủ để kết luận AI luôn cải thiện học tập. Cần dữ liệu nhiều học sinh, nhóm so sánh và đánh giá năng lực thật.",
        "evidence": "Kết luận nhân quả cần dữ liệu đủ lớn, thiết kế so sánh và kiểm soát biến gây nhiễu.",
    },
    {
        "id": "error-level-4",
        "level": 4,
        "level_name": "Thiên lệch",
        "question": "Có nên dùng AI trong giáo dục?",
        "ai_answer": "AI trong giáo dục chỉ gây hại vì học sinh sẽ lười suy nghĩ, gian lận nhiều hơn và giáo viên mất vai trò. Do đó mọi trường học nên cấm AI.",
        "error_type": "Thiên lệch",
        "suspicious_text": "chỉ gây hại",
        "corrected_answer": "AI có cả lợi ích và rủi ro. Cần quy định cách dùng, yêu cầu kiểm chứng, bảo vệ dữ liệu và giữ vai trò hướng dẫn của giáo viên.",
        "evidence": "Một đánh giá cân bằng phải xét cả hỗ trợ học tập, cá nhân hóa, nguy cơ phụ thuộc, gian lận và quyền riêng tư.",
    },
    {
        "id": "error-level-5",
        "level": 5,
        "level_name": "Nguồn giả",
        "question": "UNESCO nói gì về AI trong giáo dục?",
        "ai_answer": "Báo cáo UNESCO 'Full Automation of Schools 2025' khuyến nghị các nước thay giáo viên bằng chatbot trong vòng 3 năm.",
        "error_type": "Nguồn không tồn tại",
        "suspicious_text": "Full Automation of Schools 2025",
        "corrected_answer": "Cần kiểm tra tên báo cáo và nội dung chính thức. UNESCO thường nhấn mạnh cách tiếp cận lấy con người làm trung tâm, có giám sát và trách nhiệm.",
        "evidence": "Nguồn được nêu có dấu hiệu bịa đặt; cần đối chiếu trên trang tài liệu chính thức.",
    },
    {
        "id": "error-level-6",
        "level": 6,
        "level_name": "Rất thuyết phục",
        "question": "AI có làm giảm tư duy phản biện của học sinh không?",
        "ai_answer": "AI chắc chắn làm giảm tư duy phản biện vì khi có đáp án nhanh, học sinh sẽ không còn động cơ suy nghĩ. Do đó, mọi nghiên cứu nghiêm túc đều đi đến kết luận rằng nên tránh AI trong học tập.",
        "error_type": "Khái quát hóa + thiên lệch",
        "suspicious_text": "mọi nghiên cứu nghiêm túc",
        "corrected_answer": "Tác động của AI phụ thuộc cách thiết kế hoạt động học. Nếu học sinh phải trả lời trước, kiểm chứng, phản biện và phản tư, AI có thể trở thành công cụ rèn tư duy thay vì thay thế tư duy.",
        "evidence": "Không nên dùng cụm tuyệt đối như 'chắc chắn' hoặc 'mọi nghiên cứu' khi chưa có bằng chứng hệ thống.",
    },
]


def get_trust_item(index=0):
    return TRUST_ITEMS[index % len(TRUST_ITEMS)]


def get_compare_item(index=0):
    return COMPARE_ITEMS[index % len(COMPARE_ITEMS)]


def get_error_item(level=1):
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 1
    for item in ERROR_ITEMS:
        if item["level"] == level:
            return item
    return ERROR_ITEMS[0]


def score_trust(initial, revised, ground_truth):
    try:
        initial = int(initial)
    except (TypeError, ValueError):
        initial = 50
    try:
        revised = int(revised)
    except (TypeError, ValueError):
        revised = 50
    try:
        ground_truth = int(ground_truth)
    except (TypeError, ValueError):
        ground_truth = 50

    initial_error = abs(int(initial) - int(ground_truth))
    revised_error = abs(int(revised) - int(ground_truth))
    improvement = initial_error - revised_error
    score = max(0, min(100, 100 - revised_error + max(0, improvement // 2)))
    return {
        "initial_error": initial_error,
        "revised_error": revised_error,
        "improvement": improvement,
        "score": score,
    }


def public_trust_item(item, include_evidence=True):
    public = {
        "id": item["id"],
        "question": item["question"],
        "ai_answer": item["ai_answer"],
    }
    if include_evidence:
        public["evidence"] = item["evidence"]
    return public


def public_error_item(item):
    return {
        "id": item["id"],
        "level": item["level"],
        "level_name": item["level_name"],
        "question": item["question"],
        "ai_answer": item["ai_answer"],
    }
