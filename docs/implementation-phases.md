# Triển khai yêu cầu điều chỉnh website

## Giai đoạn 1 – Nền tảng và tài khoản

- Khôi phục 69 file ứng dụng bị thiếu từ đúng blob mà Git index ghi nhận, sau khi tải object từ origin. Giữ nguyên các file hiện có; không reset index, không commit hay đẩy mã lên remote.
- Ẩn chọn vai trò/đăng nhập sau khi có phiên; menu tên tài khoản có đăng xuất và đường dẫn theo vai trò.
- Đăng ký yêu cầu trường, lớp, giáo viên. Tài khoản cũ cập nhật tại `/app/learning-profile`.
- Bỏ thao tác tự xóa dữ liệu học sinh khi khởi động ứng dụng.
- Kiểm tra chủ sở hữu bài tập/bài nộp khi giáo viên sửa/chấm; chỉ hiện nội dung của giáo viên đó.

## Giai đoạn 2 – Chấm điểm và phản hồi phát triển tư duy

- Đánh giá lập luận: giải thích đáp án ở phía giáo viên; trả đúng/sai và nhận xét theo lý do lựa chọn, câu viết lại. Bỏ điểm theo số ký tự.
- Thám tử: 5 tiêu chí, 20 điểm/tiêu chí; trạng thái/nhận xét riêng, phản hồi học tập, phản tư, làm lại giữ bài và ẩn lời giải, nút lấy lời giải riêng sau khi nộp. Không tự chèn đáp án vào bài làm.
- Bản đồ: gợi mở theo vai trò logic, mức 0–40/60/80/100; 100 điểm có câu hỏi phản tư. Gói mới yêu cầu đúng 5 vai trò; gói cũ khác số lượng vẫn tính tỷ lệ để giữ tương thích.
- Chatbot nhiệm vụ dùng lịch sử máy chủ và bảo đảm có câu hỏi mới nhất; gợi ý dự phòng thay đổi theo nhóm câu hỏi. Kiểm tra quyền sở hữu phiên làm bài, không nhận hội thoại giả từ trình duyệt để đánh giá bài.
- Nhận xét nhiệm vụ yêu cầu chi tiết từ bài, bằng chứng, suy luận/giả định, phản biện và câu hỏi tự điều chỉnh; không suy đoán phụ thuộc AI từ số lượt chat.
- Prompt phản biện, đấu trường và AI cố tình sai dùng rubric nội dung thay vì độ dài. Không xếp thắng/thua hoặc đổi rank nếu AI chưa đánh giá được.
- AI lỗi hoặc JSON không hợp lệ: điểm tự luận chờ đánh giá, gợi ý tự học riêng từng tiêu chí; không ghi điểm chưa hoàn chỉnh vào hồ sơ năng lực. Nhận xét AI là sơ bộ, giáo viên chốt kết quả.

## Giai đoạn 3 – Thống kê và kiểm tra

- Tổng quan giáo viên thay nội dung cũ bằng biểu đồ tự đánh giá 5 nhóm kỹ năng và đánh giá chatbot.
- Lọc theo trường/lớp trong phạm vi giáo viên; 7 hoặc 30 ngày gần nhất. Tính mỗi HS một lần tự đánh giá mới nhất trong kỳ, mỗi HS/mô-đun một bình chọn chatbot mới nhất.
- Trường/lớp/giáo viên được lưu cùng lượt khảo sát để giữ bối cảnh tại thời điểm trả lời. Học sinh chọn giáo viên phụ trách; chưa có quy trình duyệt danh sách lớp chính thức.
- Dữ liệu trong `learning_surveys.json`, tương thích dữ liệu cũ; không tự gán lớp cho các tài khoản chưa khai báo.
- Kiểm tra hồi quy bằng `python -m unittest discover -s tests -v`, kiểm tra cú pháp JS và kiểm tra luồng trình duyệt trên dữ liệu tạm.
- Kết quả: 22 kiểm tra hồi quy đạt; kiểm tra trình duyệt Chrome đạt các luồng đăng ký, menu tài khoản, khảo sát, đánh giá lập luận, Thám tử (lời giải/làm lại), kéo thả bản đồ, bình chọn chatbot và biểu đồ GV. Không lỗi JavaScript; kiểm tra không tràn ngang ở chiều rộng 1365px và 390px.
- Kết nối Gemini thật bằng nội dung mẫu đã thành công; một lần chấm có cấu trúc trả đủ tiêu chí/điểm/nhận xét hợp lệ. Các kiểm tra tự động dùng phản hồi mô phỏng để kết quả có thể lặp lại.
- Chạy kiểm tra trình duyệt tùy chọn: `python tests/browser_smoke.py` (cần `playwright` và Chrome; có thể chọn trình duyệt bằng biến `BROWSER_CHANNEL`).
- Kết quả tranh biện được lưu phía máy chủ để nhận xét dài không làm vượt giới hạn cookie phiên. Lượt khảo sát mới được ghi theo giao dịch trong cấu hình một worker nhiều thread hiện tại.

## Cơ sở bảng tự đánh giá

Tham khảo mô tả năm nhóm kỹ năng Watson–Glaser tại https://www.assessmentday.co.uk/watson-glaser-critical-thinking.htm (truy cập ngày 20/10/2026): suy luận, nhận diện giả định, suy diễn, diễn giải, đánh giá lập luận.

Năm câu hỏi và thang tự nhận định 1–5 do dự án tự biên soạn; không sao chép bộ câu hỏi thương mại và chưa được thẩm định tâm trắc. Giao diện ghi rõ đây **không phải điểm WGCTA chuẩn hóa**. Cần thay cấu hình câu hỏi/cách tính khi có bộ đo chính thức được phép sử dụng. Không dùng trung bình tự nhận định để kết luận mức năng lực thực tế.
