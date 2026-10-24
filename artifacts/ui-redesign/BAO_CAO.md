# Đổi giao diện theo prompt — 24/10/2026

## Phạm vi

Áp dụng hệ thống giao diện cho đăng nhập/đăng ký, học sinh, giáo viên, quản trị và đấu trường. Giữ nguyên trang chủ ở cả `/` và `/app`: không nạp CSS/JS mới, giữ nguyên template và tài nguyên cũ. Không sửa route, API, dịch vụ chấm bài, schema, dữ liệu bài làm hoặc tài khoản.

## Bước 0 — Hiện trạng và vấn đề

| Nguồn | Hiện trạng | Vấn đề |
| --- | --- | --- |
| `app/static/css/main.css` | Nhiều lượt ghi đè; màu ghi trực tiếp; biến màu san hô, xanh, vàng và notebook riêng | Khó đồng bộ, nút chính màu đỏ/cam, nền trang thiếu nhất quán |
| `app/static/css/workshop.css` | Bảng màu riêng cho Prompt/nhiệm vụ; nhiều chữ 10–14px | Khác các mô-đun còn lại, nội dung nhỏ |
| `app/static/css/learning-feedback.css` | Ghi đè màu bong bóng hội thoại | Màu chat cần khớp hệ thống chung |
| `app/templates/base.html` | Nạp 4 font; 2 bộ icon; nút quay lại tự thêm cho mô-đun | Font/icon thiếu thống nhất; nút quay lại trùng template |
| Các template mô-đun | Sidebar lặp, phần lớn chỉ hiện số | Khó nhận diện đích điều hướng |
| `teacher_dashboard.html` | Nhiều biểu mẫu theo trang; nhãn phụ thuộc placeholder; danh sách dài | Khó quét nội dung và tìm bài |
| `admin_dashboard.html`, `gemini_lab.html` | Một số nhãn tiếng Anh; khung kết quả trống | Chưa cùng khung giáo viên, khó hiểu khi chưa có phản hồi |
| `app/static/js/main.js`, `workshop.js`, `learning-feedback.js` | Giữ API/state hiện có; một số phần tử tạo động | Cần chuẩn hóa hiển thị mà không đổi luồng nghiệp vụ |

## Bước 1 — Token

Thêm `app/static/css/design-tokens.css`: màu nền kem, bề mặt, chữ, primary xanh, AI tím, trạng thái, dark mode, font, spacing, radius, shadow và transition. Ánh xạ biến màu cũ sang token mới cho trang áp dụng. Trang chủ tiếp tục dùng bảng màu cũ.

## Bước 2 — Component

Thêm `app/static/css/design-system.css` và `app/static/js/design-system.js`. Chuẩn hóa nút, form, card, trạng thái rỗng, bộ chọn vai trò, toast từ thông báo sẵn có, đếm ký tự, số trên thanh trượt, màu phân loại bản đồ, focus ring, reduced motion và khung phản hồi Gemini. Dùng cascade layer để kiểm soát các quy tắc `!important` của CSS cũ. Chuyển icon Tabler trong trang áp dụng sang Lucide khi khởi tạo; giữ nguyên hook của JS nghiệp vụ.

## Bước 3 — Khung

- Topbar hiện trên mô-đun, một breadcrumb và một liên kết về trang chủ.
- Menu mô-đun mở được, hiển thị tên thay vì chỉ số.
- Sidebar giáo viên rộng 240px, nhóm Tổng quan / Nội dung / Theo dõi; drawer dưới 1024px.
- Quản trị và kiểm tra Gemini dùng cùng sidebar/component.
- Đấu trường dùng token tối của cùng hệ thống.
- Trang chủ không nạp bất kỳ tài nguyên giao diện mới nào.

## Bước 4 — Các màn hình

- Đăng nhập: cùng endpoint `/login` hiện có, bộ chọn vai trò ba nút điều khiển select gốc; giữ chuyển hướng đăng nhập giáo viên/quản trị sẵn có.
- Đăng ký: ba nhóm trường, nút hiện/ẩn mật khẩu sẵn có.
- Kho đề/bản đồ/lĩnh vực và danh sách giáo viên: tìm nội dung, sắp xếp tiếng Việt, đếm kết quả, xóa tìm kiếm.
- Nhiệm vụ/Prompt: chữ dễ đọc, đề trong card nền nhạt, đếm ký tự, thanh lưu nháp/nộp bài của nhiệm vụ được giữ phía dưới khi cuộn.
- Hội thoại: màu người dùng xanh, AI tím nhạt, ô nhập bám dưới trong vùng hội thoại.
- Đồng ý làm bài: card rộng hơn, nút Tôi đồng ý, focus trap; ESC/Đóng quay về danh sách, không bỏ qua việc đồng ý.
- Bản đồ: màu theo loại, nhãn chữ sẵn có, huy hiệu điểm lớn.
- Hồ sơ: radar lớn hơn trên desktop, co theo chiều rộng điện thoại; thanh điểm xanh.
- Ba bài tập ẩn: thống nhất hai cột desktop/một cột điện thoại, hiển thị số trên thanh trượt.
- Giáo viên: ba thẻ tổng hợp dùng dữ liệu sẵn có; bài nộp mở ra hai cột bài làm/chấm; form nhiệm vụ có xem trước từ nội dung đang nhập, nút lưu/đóng.
- Đấu trường: màu tối đồng bộ, đồng hồ lớn, khung đối thủ có lời nhắc khi trống.

## Bước 5 — Kiểm tra và giới hạn

- `python -m unittest discover -s tests -q`: 33 kiểm thử đạt.
- `python -u -X utf8 scripts/verify_redesign.py`: 40 đường dẫn × 4 kích thước = 160 lần mở; không có lỗi JavaScript ghi nhận; không có document tràn ngang. Xem `browser-review.json`.
- `python -u -X utf8 scripts/verify_redesign.py --states`: 14 lượt kiểm tra trạng thái ở 360/1440px, đạt; kiểm tra chọn vai trò, đồng ý làm bài, lưu nháp, xem trước nhiệm vụ và mở khung chấm. Không phát hiện lỗi JavaScript hoặc tràn ngang. Xem `state-review.json`.
- Kích thước: 360, 768, 1024, 1440px. Các trạng thái cùng URL không được tính là đường dẫn khác nhau.
- Script dùng dữ liệu sao chép tạm, không gọi dịch vụ AI để tạo phản hồi, không thay đổi bài làm thật.
- Ảnh kiểm tra trong thư mục này và `XEM_GIAO_DIEN.html`. Mã nguồn đầy đủ của các file thay đổi trong `MA_NGUON_DAY_DU.md`.

### Checklist thực tế

| Yêu cầu | Kết quả |
| --- | --- |
| Token dùng chung | Đạt cho lớp giao diện mới. CSS cũ vẫn còn hard-code để giữ nguyên trang chủ; chưa đạt yêu cầu xóa mọi hard-code toàn repository. |
| Nút chính xanh, màu lỗi/xóa riêng | Đã áp dụng trong hệ thống mới. |
| Font và cỡ nội dung | Trang thay đổi dùng Be Vietnam Pro; nội dung chính 16px, metadata nhỏ hơn. Trang chủ giữ nguyên theo yêu cầu. |
| Một primary nổi bật | Lớp trình bày giảm nhấn các nút primary phụ khi mở trang/details; chưa kiểm chứng mọi tổ hợp trạng thái động. |
| Các khu vực đồng bộ, đấu trường tối | Đã áp dụng. |
| Đăng nhập thống nhất, quay lại không chồng | Đã áp dụng trên endpoint đăng nhập chung sẵn có. |
| Trạng thái rỗng/loading | Bổ sung cho danh sách được chuẩn hóa; giữ loading hiện có và phản chiếu disabled bằng spinner. Chưa thêm skeleton cho mọi nguồn tải. |
| Tiếng Việt/icon | Chuẩn hóa các nhãn được sửa; tên kỹ thuật Gemini/API vẫn ở cấu hình. Chưa đảm bảo mọi chuỗi trả về từ server/dịch vụ AI đều được Việt hóa. |
| Luồng chính | 33 kiểm thử nghiệp vụ đạt; trình duyệt kiểm tra hiển thị và một số tương tác. Chưa kiểm tra đầu cuối với dịch vụ AI thật, giọng nói hoặc nhiều người dùng đồng thời. |
| Responsive | 160 lần mở không phát hiện tràn ngang. Không thay thế đánh giá thủ công mọi nội dung phát sinh. |
| Tương phản WCAG AA | Token chữ và nền đã chọn theo yêu cầu; đã sửa các nhãn tối ở đấu trường. Chưa chạy kiểm định AA tự động toàn bộ trạng thái. |

### Phần cần dữ liệu/chức năng chưa có

Chưa thêm độ khó, thời gian dự kiến, tiến độ và trạng thái làm bài cho mọi thẻ khi dữ liệu tương ứng không được truyền vào trang. Chưa tạo so sánh năng lực kỳ trước hoặc bộ lọc lớp/trạng thái bài nộp từ dữ liệu không có trên giao diện. Không tự bịa metadata, không đổi nghiệp vụ hoặc API để phục vụ giao diện. Chức năng lưu nháp tiếp tục dùng cơ chế hiện có của nhiệm vụ; chưa bổ sung cơ chế lưu nháp mới cho từng mô-đun khác.

Các giới hạn này có nghĩa là bản triển khai chưa đáp ứng 100% từng mục của prompt.
