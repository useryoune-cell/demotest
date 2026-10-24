"""Review teacher charts using a disposable runtime copy."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.services.storage import data_dir
from app.services.learning_analytics import learning_overview
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server, WSGIRequestHandler


class Quiet(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


def run():
    output = Path('artifacts/teacher-statistics')
    output.mkdir(parents=True, exist_ok=True)
    app = create_app()
    with app.app_context():
        source = Path(data_dir())
    errors, checks = [], []
    with tempfile.TemporaryDirectory(prefix='teacher-charts-') as temporary:
        for file in source.glob('*.json'):
            shutil.copy2(file, Path(temporary) / file.name)
        app.config.update(DATA_DIR=temporary, TESTING=True, GEMINI_API_KEYS=[])
        with app.app_context():
            expected = learning_overview('YT.PhamThiHang', 'all', class_name='11A7')['quantity']
        server = make_server('127.0.0.1', 0, app, threaded=True, request_handler=Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                context = browser.new_context(reduced_motion='reduce')
                value = app.session_interface.get_signing_serializer(app).dumps({'role':'teacher','teacher_username':'YT.PhamThiHang','teacher_name':'Phạm Thị Hằng'})
                context.add_cookies([{'name':'session','value':value,'url':base}])
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                for width in [360, 768, 1024, 1440]:
                    page.set_viewport_size({'width':width,'height':1000})
                    response = page.goto(base + '/teacher/overview?period=all&class_name=11A7', wait_until='networkidle')
                    assert response.status == 200
                    assert page.locator('#quantityStatistics .ui-metric strong').all_text_contents() == [str(expected['total_students']), str(expected['total']), str(expected['reviews']['pending'])]
                    assert page.locator('.stats-day').count() == len(expected['days'])
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    if width in [360, 1440]:
                        page.screenshot(path=str(output / f'{width}-bieu-do-giao-vien.png'), full_page=True)
                    checks.append({'width':width,'students':expected['total_students'],'activities':expected['total'],'synthetic':expected['synthetic'],'pending':expected['reviews']['pending']})
                page.goto(base + '/teacher/overview?period=week&class_name=missing', wait_until='networkidle')
                assert page.locator('#quantityStatistics .ui-metric strong').all_text_contents() == ['0','0','0']
                assert page.locator('.stats-day').count() == 7
                page.locator('select[name=class_name]').select_option('11A7')
                page.locator('select[name=period]').select_option('all')
                page.get_by_role('button', name='Xem thống kê', exact=True).click()
                page.wait_for_url('**#quantityStatistics')
                assert page.locator('#quantityStatistics .ui-metric strong').nth(1).inner_text() == str(expected['total'])
                assert not errors, errors
                browser.close()
        finally:
            server.shutdown()
            thread.join()
    report = {'checks':checks, 'browser_errors':errors,'empty_state':True,'filter_submit':True}
    (output / 'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    run()
