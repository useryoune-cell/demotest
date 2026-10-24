"""Exercise workshop interactions on disposable data and capture review screenshots."""
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from app.services.prompt_service import RUBRIC
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server


def run():
    output = Path(__file__).resolve().parents[1] / 'instance/ui-preview'
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='workshop-browser-') as directory:
        app.config.update(TESTING=True, DATA_DIR=directory, GEMINI_API_KEYS=[])
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                page = browser.new_page(viewport={'width': 1365, 'height': 1000})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))

                def fits():
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), page.url

                page.goto(base + '/app/modules/nhiem-vu')
                page.locator('[data-task-filter=history]').click()
                assert page.locator('[data-task-topic]:visible').count() == 8
                page.locator('#assignmentSearch').fill('xiem')
                assert page.locator('[data-task-topic]:visible').count() == 1
                page.locator('#assignmentSearch').fill('nonexistent topic')
                assert page.locator('#assignmentSearchEmpty').is_visible()
                page.locator('#assignmentClearSearch').click()
                assert page.locator('[data-task-topic]:visible').count() == 10
                fits()
                page.screenshot(path=str(output / 'assignments-desktop.png'), full_page=True)

                page.goto(base + '/app/modules/nhiem-vu/tasks/datatm-task-01')
                page.locator('#acceptAssignmentConsent').click()
                page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                draft = 'Em chỉ đồng ý một phần vì cải cách trong nước tạo điều kiện cho ngoại giao.'
                page.locator('#assignmentAnswer').fill(draft)
                page.locator('#assignmentSaveDraft').click()
                assert 'Đã lưu' in page.locator('#assignmentDraftStatus').inner_text()
                page.reload()
                page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                assert page.locator('#assignmentAnswer').input_value() == draft
                fits()
                page.screenshot(path=str(output / 'assignment-work-desktop.png'), full_page=True)
                page.locator('#assignmentChatToggle').click()
                assert page.locator('#assignmentChatPanel').is_visible()
                page.locator('#assignmentChatClose').click()
                assert 'AI hỗ trợ em suy nghĩ' in page.locator('#assignmentChatToggle').inner_text()
                # A successful submission removes only this student's task draft.
                page.locator('#assignmentAnswer').fill('Em đối chiếu bằng chứng trong sách giáo khoa. ' * 21)
                page.locator('#assignmentForm button[type=submit]').click()
                page.wait_for_function("!document.querySelector('#assignmentResult').hidden")
                assert page.evaluate("Object.keys(localStorage).filter(k => k.startsWith('learning-draft:')).length") == 0

                page.goto(base + '/app/modules/prompt-phan-bien')
                original = 'Đóng vai nhà nghiên cứu lịch sử, kiểm chứng bằng chứng, phản biện ý kiến trái chiều và điều chỉnh kết luận.'
                page.locator('#criticPrompt').fill(original)
                assert page.locator('#promptStructureCount').inner_text() == '4/4 bước'
                app.config['GEMINI_API_KEYS'] = ['browser-test']
                fixture = {'rubric': [{'key': r['key'], 'score': [25, 14, 5, 20][i], 'status': 'Đúng', 'feedback': 'Hãy làm rõ nguồn và mức độ chắc chắn.'} for i, r in enumerate(RUBRIC)],
                           'feedback': 'Em đã yêu cầu đối chiếu và xem xét ý kiến trái chiều.', 'reflection': 'Nguồn nào sẽ giúp em điều chỉnh kết luận?'}
                fake = SimpleNamespace(generate_text=lambda *args, **kwargs: SimpleNamespace(text=json.dumps(fixture)))
                with patch('app.services.learning_feedback.GeminiClient.from_app_config', return_value=fake):
                    page.locator('#promptCriticForm button[type=submit]').click()
                    page.wait_for_function("!document.querySelector('#promptRubric').hidden")
                statuses = page.locator('.prompt-rubric-row div > span').all_text_contents()
                assert set(statuses) == {'Đạt', 'Chưa rõ', 'Cần bổ sung'}, statuses
                page.locator('#promptRewrite').click()
                assert page.locator('#promptPreviousText').text_content() == original
                assert page.locator('#criticPrompt').input_value() == original
                fits()
                page.screenshot(path=str(output / 'prompt-desktop.png'), full_page=True)
                page.locator('#promptScenario').select_option('balanced-ai-policy')
                assert 'bài tập về nhà' in page.locator('#promptSituation').inner_text()
                assert not page.locator('#promptRubric').is_visible()
                assert page.locator('#promptRewrite').is_disabled()
                for width in [768, 390]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    for label, url in [('prompt', '/app/modules/prompt-phan-bien'), ('assignments', '/app/modules/nhiem-vu'), ('assignment-work', '/app/modules/nhiem-vu/tasks/datatm-task-01')]:
                        page.goto(base + url)
                        if label == 'assignment-work':
                            page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                        fits()
                        page.screenshot(path=str(output / f'{label}-{width}.png'), full_page=True)
                assert not errors, errors
                browser.close()
                print('PASS: search/filter, drafts, submit, chat, four prompt criteria, rewrite and responsive layouts at 1365/768/390px')
                print('Screenshots:', output)
        finally:
            server.shutdown()
            thread.join()


if __name__ == '__main__':
    run()
