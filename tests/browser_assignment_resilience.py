"""Local mobile regression checks with disposable data and intercepted failures."""
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server


def run():
    with tempfile.TemporaryDirectory(prefix='assignment-regression-') as directory:
        app.config.update(TESTING=True, DATA_DIR=directory, GEMINI_API_KEYS=[])
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                page = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(base + '/app/modules/nhiem-vu/tasks/task-source-checking-short-essay')
                page.route('**/api/modules/assignments/start', lambda route: route.abort('failed'))
                page.locator('#acceptAssignmentConsent').click()
                page.wait_for_function("!document.querySelector('#acceptAssignmentConsent').disabled")
                assert page.locator('#assignmentConsent').is_visible()
                page.unroute('**/api/modules/assignments/start')
                page.locator('#acceptAssignmentConsent').click()
                page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                assert not page.locator('.module-focus-back').is_visible()
                answer = page.locator('#assignmentAnswer')
                answer.fill('word ' * 19)
                assert not answer.evaluate('(el) => el.checkValidity()')
                answer.fill('word ' * 200)
                assert answer.evaluate('(el) => el.checkValidity()')

                # Verify server validation independently of the browser constraint.
                task_id = 'task-source-checking-short-essay'
                attempt = page.request.post(base + '/api/modules/assignments/start', data={'task_id': task_id}).json()['attempt']
                for words in (19, 221):
                    result = page.request.post(base + '/api/modules/assignments/submit', data={
                        'task_id': task_id, 'attempt_id': attempt['id'], 'answer': 'word ' * words})
                    assert result.status == 400

                page.route('**/api/modules/assignments/submit', lambda route: route.abort('failed'))
                page.locator('#assignmentForm button[type=submit]').click()
                page.wait_for_function("!document.querySelector('#assignmentForm button[type=submit]').disabled")
                assert page.locator('#assignmentMeta').inner_text() != 'Đang nộp bài...'
                assert answer.input_value().strip() == ('word ' * 200).strip()

                page.locator('#assignmentChatToggle').click()
                assert not page.locator('#assignmentChatToggle').is_visible()
                assert page.locator('#assignmentChatClose').is_visible()
                page.route('**/api/modules/assignments/chat', lambda route: route.fulfill(
                    status=500, content_type='text/html', body='<h1>Internal Server Error</h1>'))
                page.locator('#assignmentChatInput').fill('Test question')
                page.locator('#assignmentChatForm button[type=submit]').click()
                page.wait_for_function("!document.querySelector('#assignmentChatInput').disabled")
                assert page.locator('#assignmentChatInput').input_value() == 'Test question'
                assert 'JSON' not in page.locator('#assignmentChatThread').inner_text()
                bubble = page.locator('#assignmentChatThread .user p').last
                assert bubble.evaluate('(el) => getComputedStyle(el).color') == 'rgb(255, 255, 255)'
                page.unroute('**/api/modules/assignments/chat')
                with page.expect_response('**/api/modules/assignments/chat') as chat_response:
                    page.locator('#assignmentChatForm button[type=submit]').click()
                assert chat_response.value.status == 200
                assert chat_response.value.json()['meta']['model'] == 'fallback'
                page.wait_for_function("!document.querySelector('#assignmentChatInput').disabled")
                assert page.locator('#assignmentChatInput').input_value() == ''
                page.locator('#assignmentChatClose').click()
                assert page.locator('#assignmentChatToggle').is_visible()
                page.goto(base + '/app/modules/prompt-phan-bien')
                prompt = page.locator('#criticPrompt')
                prompt.fill('Verify this historical claim with evidence and opposing views.')
                page.route('**/api/modules/prompt/score', lambda route: route.fulfill(
                    status=500, content_type='text/html', body='<h1>Error</h1>'))
                page.locator('#promptCriticForm button[type=submit]').click()
                page.wait_for_function("!document.querySelector('#promptCriticForm button[type=submit]').disabled")
                assert page.locator('#promptScoreMeta').inner_text()
                assert prompt.input_value().startswith('Verify')
                page.unroute('**/api/modules/prompt/score')
                page.locator('#promptCriticForm button[type=submit]').click()
                page.wait_for_function("!document.querySelector('#promptRubric').hidden")
                assert page.locator('#promptSuggestion').inner_text()
                assert not errors, errors
                browser.close()
                print('PASS: assignment start retry, mobile layout, submit/chat errors and prompt error recovery')
        finally:
            server.shutdown()
            thread.join()


if __name__ == '__main__':
    run()
