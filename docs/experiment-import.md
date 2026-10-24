# Nạp tài khoản và dữ liệu mô phỏng ngày 24/10/2026

Nguồn tài khoản là hai Excel trong `capnhat`. Mật khẩu chung lấy từ
`capnhat/ghichu.txt`, giữ nguyên chữ hoa/thường theo ghi chú, không theo cột mật
khẩu trong Excel. Không thay đổi tài khoản cũ ngoài đợt nạp này.

Phân công theo thứ tự được người dùng đồng ý:

| Lớp | Số HS | Giáo viên |
| --- | ---: | --- |
| 11A7 | 50 | Phạm Thị Hằng (`YT.PhamThiHang`) |
| 11A8 | 48 | Lê Ngọc Hà (`YT.LeNgocHa`) |

Nguyễn Thị Hồng Như và Hoàng Thị Tỉnh được nạp tài khoản, chưa có lớp phụ trách.

## Số lượng mỗi học sinh

Lấy 20% **số bài khác nhau đang mở**, làm tròn lên. Chỉ chọn bài Lịch sử 11 từ
ngân hàng DATATM đã có trong dự án. Mỗi bài có hai lượt: bài ban đầu và bài sửa.
Một phần lượt sửa giữ nguyên hoặc giảm nhẹ điểm; không giả định mọi HS tiến bộ.

| Mô-đun | Tổng số bài đang mở | Số bài/HS | Số lượt/HS |
| --- | ---: | ---: | ---: |
| Nhiệm vụ học tập | 10 | 2 | 4 |
| Thám tử thông tin | 16 | 4 | 8 |
| Đánh giá lập luận AI | 22 | 5 | 10 |
| Bản đồ lập luận | 25 | 5 | 10 |
| Prompt phản biện | 2 | 1 | 2 |

Do làm tròn, 1/2 tình huống Prompt tương ứng 50%; không thể lấy chính xác 20%
của hai tình huống. Tổng cộng 17 bài khác nhau, 34 lượt làm mỗi HS; 3.332 lượt
cho 98 HS. Hai lượt cùng bài có liên kết để đối chiếu.

Socratic là đối thoại tự do, Nhật ký và Hồ sơ không có ngân hàng bài hữu hạn để
tính 20%. Mỗi HS có thêm một phiên Socratic sáu giai đoạn (12 tin nhắn) về một
chủ đề trong ngân hàng SGK và một nhật ký phản tư tương ứng. Hồ sơ tổng hợp từ
hoạt động đã lưu. Không sinh bài cho các mô-đun đang ẩn, không tạo phiếu khảo
sát hoặc bình chọn chatbot thay HS.

## Nguồn và ý nghĩa dữ liệu

Toàn bộ bài làm, điểm, nhận xét, hội thoại và thời gian làm trong đợt nạp được
gắn `synthetic: true`, `import_batch: capnhat-simulation-v1`; đây **không phải
kết quả học sinh làm thật, dữ liệu nghiên cứu hay bằng chứng hiệu quả dạy học**.
Tài khoản và tên/lớp lấy từ Excel; nhãn mô phỏng áp dụng cho hoạt động được sinh.

Nội dung dựa trên dữ kiện, rubric và đáp án DATATM đã nạp trong dự án, có dẫn
SGK Lịch sử 11 Kết nối tri thức. Chưa OCR hoặc kiểm chứng từng trang của hai PDF
trong `capnhat`. Bộ sinh dùng mẫu câu và dữ kiện có sẵn, không gọi AI để chấm
hoặc giả danh nhận xét giáo viên. Điểm/nhận xét chốt của GV để trống.

Hồ sơ hiển thị nhãn mô phỏng, nội dung bài, nhận xét và tối đa 200 hoạt động gần
nhất. Biểu đồ lấy bảy điểm đã lưu gần nhất thay vì ghép sáu số 0 với phần trăm
hoàn thành. Điểm các bài khác nhau không phải thang đo tiến bộ chuẩn hóa.

## Công cụ và sao lưu

Chạy xem trước: `python -X utf8 scripts/import_experiment.py`.
Nạp: `python -X utf8 scripts/import_experiment.py --apply`.

Đích ghi lấy theo `DATA_DIR` của ứng dụng. Trước khi ghi, chương trình kiểm tra
dữ liệu chưa thay đổi từ lúc đọc, sao lưu đủ các tệp bị tác động vào
`DATA_DIR/backups/capnhat-simulation-v1-<timestamp>/`. Nếu ghi thất bại, khôi phục
các tệp ban đầu. Có manifest `DATA_DIR/experiment-import.json` chứa số lượng,
phân công, dấu kiểm tra nguồn và đường dẫn sao lưu; không ghi mật khẩu vào manifest.
Một đợt đã nạp không được ghi đè hoặc nạp trùng.

Kiểm tra: `python -m unittest discover -s tests -v`. Kiểm tra nạp dùng thư mục
tạm, kiểm tra quota của cả 98 HS, đăng nhập, giữ tài khoản cũ, sao lưu, chống
trùng, điểm bản đồ, độ dài bài và quyền xem bài nộp theo GV.
