# Dữ liệu DATATM

Nguồn: bốn file Word trong `DATATM/`. Tạo lại ngân hàng JSON bằng:

```powershell
python -X utf8 scripts/import_datatm.py
```

Kết quả: 23 bản đồ lập luận, 20 bài so sánh ba câu trả lời AI, 8 nhiệm vụ học tập,
14 trạm thám tử TT01–TT14. Bốn bản lặp của nhiệm vụ 3/4 và phần hội thoại soạn
thảo không được nhập thành đề. Không viết thêm câu hỏi hoặc đáp án.

Ngân hàng nằm tại `app/data/datatm_bank.json`, ngoài thư mục public/static.
Mỗi bộ được thêm một lần vào kho dữ liệu tương ứng khi chức năng được truy cập.
Mã đề cố định và `datatm_imported_ids` giúp giữ chỉnh sửa, trạng thái ẩn và việc
xóa đề của giáo viên khi khởi động lại. Không xóa đề cũ, bài nộp hoặc lịch sử.
Các đề nhập được gán cho tài khoản giáo viên có sẵn `teacher01`.

Rubric giữ thang 10 điểm theo Word. Đoạn kiến thức tham chiếu dành cho người
chấm được đặt trong rubric, không đặt trong đề học sinh. Mảnh lập luận và đáp án
A/B/C giữ nguyên theo tài liệu; số thứ tự 1/2/3 chuyển tương ứng thành A/B/C.

Loại lỗi thám tử được ánh xạ vào lựa chọn hiện có: lỗi thời gian, địa điểm,
dữ kiện hoặc nội dung → `Dữ kiện sai`; TT14 → `Khái quát hóa quá mức`. Nguyên văn
phân loại chi tiết vẫn nằm trong `source_error_type`. Không thay đổi giao diện.

Đây là nhập dữ liệu theo nguồn người dùng, chưa phải xác minh độc lập với SGK.
Tài liệu có các mốc cần giáo viên đối chiếu: bản đồ Lam Sơn ghi cuối năm 1427
quân Minh rút hết, còn TT10 ghi tháng 1/1428; bản đồ Lê Thánh Tông ghi năm 1469
đổi thành 13 đạo, còn TT05 ghi năm 1471 đặt đạo thứ 13 Quảng Nam. Dữ liệu giữ
nguyên từng tài liệu, không tự sửa các mốc này.

Kiểm tra: `python -m unittest discover -s tests -p 'test*.py'`.
