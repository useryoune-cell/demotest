"""Optional browser integration: python tests/browser_smoke.py (Playwright Chromium)."""
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from app.services.teacher_content_service import get_argument_package
from app.services.compare_assignment_service import get_compare_package
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server


def fake_generate(prompt):
    if 'DATA:\n' not in prompt:
        return SimpleNamespace(text='Hãy chọn một khẳng định và tìm nguồn độc lập để kiểm chứng.', model='browser-test', key_index=0, attempts=1)
    data = json.loads(prompt.split('DATA:\n', 1)[1])
    result = {'rubric': [{'key': c['key'], 'score': c['max'], 'status':'Đúng',
                         'feedback':'Em đã trình bày căn cứ. Hãy xét thêm một giới hạn của kết luận.'} for c in data['criteria']],
              'feedback':'Lý lẽ đã có căn cứ; hãy kiểm tra trường hợp ngoại lệ.', 'reflection':'Bằng chứng nào có thể khiến em đổi ý?'}
    return SimpleNamespace(text=json.dumps(result, ensure_ascii=False), model='browser-test', key_index=0, attempts=1)


def run():
    with tempfile.TemporaryDirectory(prefix='critical-thinking-browser-') as directory:
        app.config.update(TESTING=True, DATA_DIR=directory, GEMINI_API_KEYS=['test-only'])
        with app.app_context():
            package = get_argument_package(active_only=True)
            compare = get_compare_package()
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        errors = []
        try:
            with patch('app.services.learning_feedback.GeminiClient.from_app_config', return_value=SimpleNamespace(generate_text=fake_generate)):
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, channel=os.getenv('BROWSER_CHANNEL', 'chrome'))
                    page = browser.new_page(viewport={'width':1365, 'height':900})
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.goto(base+'/student/register')
                    for name, value in [('name','Browser Student'),('school','Browser School'),('class_name','10A'),('username','browserstudent'),('password','test-password')]:
                        page.locator(f'[name="{name}"]').fill(value)
                    page.locator('[name="teacher_username"]').select_option('teacher01')
                    page.locator('button[type="submit"]').click()
                    page.wait_for_url(base+'/app')
                    assert page.locator('.ecosystem-role-grid').count() == 0
                    page.locator('.account-menu summary').click()
                    assert page.get_by_text('Đăng xuất', exact=True).is_visible()
                    page.goto(base+'/app/learning-profile')
                    for key in ['inference','assumptions','deduction','interpretation','arguments']:
                        page.locator(f'[name="{key}"]').select_option('4')
                    page.get_by_role('button', name='Lưu tự đánh giá').click()
                    assert page.get_by_role('status').is_visible()

                    page.goto(base+f"/app/modules/so-sanh-ba-cau-tra-loi?package={compare['id']}")
                    page.locator(f'[data-answer-value="{compare["best"]}"]').click()
                    page.locator('#compareCriteria').fill('Em chọn câu này vì có giới hạn và yêu cầu đối chiếu nguồn độc lập.')
                    page.locator('#compareSynthesis').fill('Thông tin cần được kiểm chứng bằng dữ liệu gốc và nguồn độc lập trước khi rút ra kết luận có điều kiện.')
                    page.locator('#compareForm button[type="submit"]').click()
                    page.locator('#compareFeedback').wait_for()
                    assert '100/100' in page.locator('#compareFeedback').inner_text()
                    assert 'Đáp án giáo viên' in page.locator('#compareFeedback').inner_text()

                    page.goto(base+'/app/modules/tham-tu-ai?field=kiem-chung-nguon-ai')
                    page.locator('#detectiveSuspicious').fill('Global Classroom Automation Index 2026')
                    page.locator('#detectiveType').select_option(label='Nguồn không tồn tại')
                    page.locator('#detectiveExplanation').fill('Tên báo cáo và số liệu chưa có căn cứ xác nhận.')
                    page.locator('#detectiveEvidence').fill('Đối chiếu kho UNESCO, ghi rõ tài liệu và kết quả tìm kiếm; chưa xác nhận số liệu.')
                    original = 'Không sử dụng số liệu 73% khi chưa xác minh được nguồn.'
                    page.locator('#detectiveRewrite').fill(original)
                    page.locator('#detectiveForm button[type="submit"]').click()
                    page.locator('#detectiveFeedback').wait_for(state='visible')
                    assert page.locator('#detectiveFeedback article').count() == 5
                    page.get_by_role('button', name='Xem đáp án chuẩn', exact=True).click()
                    page.get_by_text('Câu viết lại tham khảo:', exact=False).wait_for()
                    assert page.locator('#detectiveRewrite').input_value() == original
                    page.get_by_role('button', name='Làm lại', exact=True).click()
                    assert page.locator('#detectiveFeedback').is_hidden()
                    assert page.locator('#detectiveRewrite').input_value() == original

                    page.goto(base+f"/app/modules/ban-do-lap-luan/maps/{package['id']}")
                    for piece in package['pieces']:
                        page.locator(f'[data-piece-id="{piece["id"]}"]').drag_to(page.locator(f'[data-bucket-key="{piece["bucket"]}"] .bucket-dropzone'))
                    page.locator('#scoreArgumentMap').click()
                    page.locator('#argumentResult').wait_for(state='visible')
                    assert page.locator('#argumentScore').inner_text() == '100/100'
                    assert page.locator('#argumentResultBadge').inner_text() == 'Thành thạo'
                    assert 'Vì sao' in page.locator('#argumentReflection').inner_text()

                    page.goto(base+'/app/modules/chatbot-socratic')
                    page.locator('.chatbot-rating select').select_option('5')
                    page.locator('.chatbot-rating button').click()
                    page.get_by_text('Đã lưu đánh giá.', exact=True).wait_for()
                    page.goto(base+'/student/logout')
                    page.goto(base+'/login?role=teacher')
                    page.locator('[name="username"]').fill('teacher01')
                    page.locator('[name="password"]').fill('teacher123')
                    page.locator('button[type="submit"]').click()
                    page.wait_for_url('**/teacher')
                    assert page.locator('meter').count() == 10
                    assert 'Browser School' in page.locator('main').inner_text()
                    assert '1 lượt đánh giá' in page.locator('main').inner_text()
                    screenshot = Path(tempfile.gettempdir())/'critical-thinking-teacher-overview.png'
                    page.screenshot(path=str(screenshot), full_page=True)
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Desktop horizontal overflow'
                    page.set_viewport_size({'width':390, 'height':844})
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile horizontal overflow'
                    assert page.locator('.account-menu summary').is_visible()
                    print('Screenshot:', screenshot)
                    assert not errors, errors
                    browser.close()
                    print('PASS: browser registration, account menu, survey, compare, detective retry/solution, map drag/drop, chatbot rating, teacher charts; no JavaScript errors.')
        finally:
            server.shutdown(); thread.join(timeout=5)


if __name__ == '__main__':
    run()
