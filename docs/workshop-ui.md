# Giao diện Prompt phản biện và Nhiệm vụ học tập

Thiết kế theo `capnhat/prompt.docx` và hai ảnh minh họa giao diện mới.

- Prompt: thẻ tình huống/mục tiêu, khung bốn bước, nhận diện cấu trúc khi gõ
  (gợi ý theo diễn đạt, không phải chấm điểm), bộ chấm nội dung bốn tiêu chí
  tổng 100 điểm, trạng thái Đạt/Chưa rõ/Cần bổ sung, giữ prompt trước khi viết
  lại. Tình huống được chọn đi cùng yêu cầu chấm AI. Nếu AI chưa chấm được,
  hiển thị chờ đánh giá; không quy về điểm đạt/chưa đạt.
- Nhiệm vụ: thẻ nội dung ngắn, lọc chủ đề, tìm kiếm không dấu và trạng thái
  không có kết quả. Màn hình làm bài tách đề, gợi ý định hướng có thể thu gọn,
  ô viết, rubric đúng theo dữ liệu của giáo viên, chatbot trong trang và phản hồi
  sau nộp. Đồng hồ vẫn ghi thời gian đã làm, không thêm hạn nộp giả.
- Lưu nháp vào trình duyệt, tách theo tài khoản và nhiệm vụ; khôi phục khi tải
  lại, xóa nháp của nhiệm vụ đó sau khi nộp thành công. Nút ghi rõ bản nháp nằm
  trên thiết bị hiện tại. Trục trặc kết nối vẫn giữ bài để gửi lại.

CSS và JavaScript riêng trong `app/static/css/workshop.css` và
`app/static/js/workshop.js`, chỉ áp dụng cho hai khu vực này.

Kiểm tra:

```text
python -m unittest discover -s tests -v
node --check app/static/js/main.js
node --check app/static/js/workshop.js
python tests/browser_assignment_resilience.py
python tests/browser_workshop.py
```

Kiểm tra trình duyệt dùng dữ liệu tạm, không thay đổi hồ sơ HS đang có.
Ảnh kiểm tra tại `instance/ui-preview/` gồm máy tính, tablet và điện thoại.
Phản hồi theo bốn tiêu chí trong kiểm tra UI dùng AI mô phỏng để kết quả ổn định; kiểm
tra Gemini thật được thực hiện riêng, không ghi thành bài của HS.
