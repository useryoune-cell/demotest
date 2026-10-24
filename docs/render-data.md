# Render: mã nguồn và dữ liệu triển khai

`app/data/deployment-seed.zip` chứa bản chụp dữ liệu JSON từ dự án: tài khoản,
bài nộp, hoạt động, phản tư và cấu hình. Mật khẩu trong bản chụp đã được băm;
đăng nhập bằng mật khẩu cũ vẫn được hỗ trợ. Dữ liệu bài làm mô phỏng giữ nguyên
nhãn và nguồn gốc, không chuyển thành dữ liệu học sinh làm thật.

Không đưa `.env`, khóa API, Excel gốc, SGK PDF, log, ảnh chụp kiểm tra hoặc bản
sao lưu cục bộ lên GitHub. Chỉ giữ tài liệu DATATM vốn đã nằm trong repo để
kiểm tra ngân hàng nội dung. Các kiểm tra Excel riêng tư được bỏ qua nếu không
có thư mục `capnhat` trên máy chạy kiểm tra.

## Tự nạp khi Render khởi động

Khi `RENDER=true`, ứng dụng đọc `SEED_DATA_BUNDLE` (mặc định là bundle trong
`app/data`) và nạp vào `DATA_DIR`. Mỗi phiên bản bundle có dấu SHA-256 để chỉ
nạp một lần trên cùng ổ dữ liệu. Với ổ đã có dữ liệu, chương trình bổ sung tài
khoản/bài nộp/hoạt động còn thiếu theo tên đăng nhập hoặc ID; tài khoản, mật
khẩu, bài làm, điểm và nhận xét đang có luôn được ưu tiên giữ lại. Nội dung
nhập bổ sung không ghi đè phần giáo viên đã chỉnh. Trước khi ghi có sao lưu;
ghi lỗi thì khôi phục. Dữ liệu hoạt động được sắp theo thời gian.

## Gói miễn phí và lưu lâu dài

Blueprint giữ `plan: free`, dùng `DATA_DIR=/tmp/critical-thinking-data` và không
khai báo disk vì Render Free không hỗ trợ disk. Bundle giúp khôi phục toàn bộ
dữ liệu đóng gói khi redeploy/cold start; **những bài mới phát sinh sau deploy
không được lưu bền vững trên gói này**. Muốn giữ dữ liệu mới qua các lần khởi
động, cần database ngoài hoặc disk trên gói hỗ trợ, rồi đặt `DATA_DIR` về đường
dẫn disk đó. Không tự thay đổi gói trả phí hay cài đặt tài khoản Render.

Nếu dịch vụ Render đã được tạo thủ công, đặt `GEMINI_API_KEYS`, `SECRET_KEY`,
`ADMIN_USERNAME`, `ADMIN_PASSWORD` trên Render; không chép chúng vào GitHub.
Python app tự nhận môi trường Render nên không cần thêm lệnh nhập dữ liệu
trong build/start command. Blueprint chỉ có hiệu lực cấu hình khi dịch vụ dùng
Blueprint hoặc đã được đồng bộ cấu hình tương ứng.

## Làm mới bundle sau này

`python scripts/export_deployment_seed.py` đọc `DATA_DIR` hiện tại, tạo bundle
mới và băm mật khẩu khi xuất; dữ liệu trên máy đang làm việc không bị đổi.
Commit/push bundle mới để Render nhận bản chụp mới. Không xuất lại bundle nếu
không cần vì mỗi lần băm sẽ tạo salt mới.

`python -m unittest discover -s tests -v` kiểm tra khởi tạo mới, xác thực bằng
hash, giữ dữ liệu có sẵn và chạy lại không nhân đôi bản ghi.
