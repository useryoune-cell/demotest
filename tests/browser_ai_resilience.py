"""Browser regression for hung requests, HTML errors, duplicate sends and retry."""
import json
from pathlib import Path
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server


def run():
    with tempfile.TemporaryDirectory(prefix='ai-resilience-') as directory:
        app = create_app()
        app.config.update(DATA_DIR=directory, GEMINI_API_KEYS=[])
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                for failure in ('timeout', 'html', 'json'):
                    page = browser.new_page()
                    page.goto(f'http://127.0.0.1:{server.server_port}/app/modules/chatbot-socratic')
                    page.clock.install()
                    requests_seen = []
                    held_routes = []
                    pattern = '**/api/modules/socratic/message'

                    def fail(route):
                        requests_seen.append(route.request.post_data_json)
                        if failure == 'html':
                            route.fulfill(status=500, content_type='text/html', body='<h1>Internal Server Error</h1>')
                        elif failure == 'json':
                            route.fulfill(status=502, json={'error': 'AI tạm thời chưa phản hồi.'})
                        else:
                            held_routes.append(route)

                    page.route(pattern, fail)
                    question = 'em chưa hiểu lắm, hãy giải thích thêm'
                    page.locator('#socraticInput').fill(question)
                    page.locator('#socraticForm button[type=submit]').click()
                    if failure == 'timeout':
                        page.wait_for_function('document.querySelector("#socraticInput").disabled')
                        page.evaluate('document.querySelector("#socraticForm").dispatchEvent(new Event("submit", {cancelable:true}))')
                        page.clock.fast_forward(45001)
                    page.wait_for_function('!document.querySelector("#socraticInput").disabled')
                    assert page.locator('#socraticInput').input_value() == question
                    assert page.locator('#socraticForm button[type=submit]').is_enabled()
                    assert page.locator('#socraticThread .loading').count() == 0
                    assert len(requests_seen) == 1
                    assert 'thử gửi lại' in page.locator('#socraticMeta').inner_text()
                    for route in held_routes:
                        route.abort()
                    page.unroute(pattern, fail)

                    def succeed(route):
                        requests_seen.append(route.request.post_data_json)
                        route.fulfill(json={'ai_message': 'Em hãy chọn một lĩnh vực để kiểm chứng.',
                            'stage_index': 0, 'stage': {'key': 'PROBE'}, 'labels': [], 'board_updates': {},
                            'meta': {'mode_label': 'Dễ tiếp cận', 'model': 'test', 'key_label': 'test'}})

                    page.route(pattern, succeed)
                    page.locator('#socraticForm button[type=submit]').click()
                    page.wait_for_function('!document.querySelector("#socraticInput").disabled')
                    assert len(requests_seen[-1]['messages']) == 2, requests_seen
                    assert 'chọn một lĩnh vực' in page.locator('#socraticThread').inner_text()
                    assert page.locator('#socraticInput').input_value() == ''
                    print('PASS:', failure, 'clears loading, preserves question, prevents duplicate request and retries')
                    page.close()
                browser.close()
        finally:
            server.shutdown()
            thread.join()


if __name__ == '__main__':
    run()
