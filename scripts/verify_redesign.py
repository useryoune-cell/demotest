"""Browser review on a temporary runtime copy; never calls the AI provider."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.services.storage import data_dir
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server, WSGIRequestHandler


class Quiet(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


def run():
    output = Path('artifacts/ui-redesign')
    output.mkdir(parents=True, exist_ok=True)
    original = create_app()
    with original.app_context():
        source = Path(data_dir())
    catalog = json.loads(Path('anh_giao_dien_website_2026-10-24/danh-muc.json').read_text(encoding='utf-8'))
    screens = [r for r in catalog['screens'] if r['device'] == 'desktop']
    # States sharing a URL are checked separately by the existing functional tests.
    routes = list({(r['role'], r['route']): r for r in screens}.values())
    state_review = '--states' in sys.argv
    if state_review:
        routes = [r for r in routes if r['id'] in ['11-nhiem-vu-mo-chat-ai','16-prompt-phan-bien','33-gv-mo-bai-nop','34-gv-mo-form-sua-nhiem-vu','35-quan-tri','43-dau-truong-lap-luan-battle','02-dang-nhap-hoc-sinh']]
    results, errors = [], []
    with tempfile.TemporaryDirectory(prefix='ui-review-') as temp:
        for file in source.glob('*.json'):
            shutil.copy2(file, Path(temp) / file.name)
        app = create_app()
        app.config.update(DATA_DIR=temp, TESTING=True, GEMINI_API_KEYS=[])
        auth = json.loads((Path(temp) / 'auth.json').read_text(encoding='utf-8'))
        student = next(s for s in auth['students'] if s.get('account_import_batch') == 'capnhat-simulation-v1')
        sessions = {
            'public': {},
            'student': {'role':'student', 'student_username':student['username'], 'student_name':student['name']},
            'teacher': {'role':'teacher', 'teacher_username':student['teacher_username'], 'teacher_name':'Giáo viên'},
            'bank_teacher': {'role':'teacher', 'teacher_username':'teacher01', 'teacher_name':'Giáo viên'},
            'admin': {'role':'admin', 'admin_username':'admin'},
        }
        server = make_server('127.0.0.1', 0, app, threaded=True, request_handler=Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                for width in ([360, 1440] if state_review else [360, 768, 1024, 1440]):
                    contexts = {}
                    for screen in routes:
                        role = screen['role']
                        if role not in contexts:
                            context = browser.new_context(viewport={'width':width,'height':1000}, reduced_motion='reduce')
                            if sessions[role]:
                                value = app.session_interface.get_signing_serializer(app).dumps(sessions[role])
                                context.add_cookies([{'name':'session','value':value,'url':base}])
                            page = context.new_page()
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            contexts[role] = (context,page)
                        page = contexts[role][1]
                        response = page.goto(base + screen['route'], wait_until='networkidle')
                        if state_review:
                            if screen['id'] == '11-nhiem-vu-mo-chat-ai':
                                modal = page.locator('#assignmentConsent')
                                if modal.is_visible():
                                    page.locator('#acceptAssignmentConsent').click()
                                    page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                                page.locator('#assignmentAnswer').fill('Bài làm kiểm tra giao diện trên bản sao dữ liệu.')
                                page.locator('#assignmentSaveDraft').click()
                                assert page.locator('#assignmentDraftStatus').inner_text()
                            if screen['id'] == '34-gv-mo-form-sua-nhiem-vu':
                                page.locator('#newAssignment').evaluate('(element) => element.open = true')
                                form = page.locator('#newAssignment .assignment-task-form')
                                form.locator('[name=title]').fill('Bản xem trước giao diện')
                                page.locator('#newAssignment .ui-preview').evaluate('(element) => element.open = true')
                                actual = page.locator('#newAssignment .ui-preview h3').first.inner_text()
                                assert actual == 'Bản xem trước giao diện', repr({'preview':actual,'errors':errors})
                            if screen['id'] == '33-gv-mo-bai-nop':
                                page.locator('.teacher-topic-editor').first.evaluate('(element) => element.open = true')
                                assert page.locator('.ui-review-grid').first.is_visible()
                            page.screenshot(path=str(output / f"{width}-{screen['id']}-state.png"),full_page=False)
                        info = page.evaluate('''() => ({width:innerWidth, document:document.documentElement.scrollWidth,
                            overflow:[...document.querySelectorAll('main *')].filter(e => e.getClientRects().length && e.getBoundingClientRect().right > innerWidth + 2).slice(0,8).map(e => e.tagName+'.'+e.className),
                            primary:[...document.querySelectorAll('.button.primary')].filter(e=>e.getClientRects().length).length,
                            color:document.querySelector('.button.primary') ? getComputedStyle(document.querySelector('.button.primary')).backgroundColor:null})''')
                        results.append({'id':screen['id'],'route':screen['route'],'width':width,'status':response.status,**info})
                        if screen['id'] in ['01-trang-chu','02-dang-nhap-hoc-sinh','08-danh-sach-nhiem-vu','16-prompt-phan-bien','24-gv-tong-quan','30-gv-bai-nop','35-quan-tri','43-dau-truong-lap-luan-battle'] and width in [360,1440]:
                            page.screenshot(path=str(output / f"{width}-{screen['id']}.png"),full_page=False)
                        if screen['id'] == '02-dang-nhap-hoc-sinh':
                            page.get_by_role('button',name='Giáo viên',exact=True).click()
                            assert page.locator('#role').input_value() == 'teacher'
                        if screen['id'] == '19-ban-do-kho-bai':
                            search = page.get_by_role('searchbox',name='Tìm trong danh sách')
                            search.fill('zzzz-no-match')
                            assert page.locator('.ui-empty').is_visible()
                        if screen['id'] == '24-gv-tong-quan' and width == 360:
                            page.get_by_role('button',name='Danh mục').click()
                            assert page.locator('.app-sidebar').is_visible()
                            page.keyboard.press('Escape')
                            assert not page.locator('.app-sidebar').is_visible()
                    print(f'Checked {width}px: {len(routes)} routes',flush=True)
                    for context,_ in contexts.values():
                        context.close()
                browser.close()
            with app.test_client() as client:
                for home in ['/', '/app']:
                    html = client.get(home).get_data(as_text=True)
                    assert 'css/design-system.css' not in html
                    assert 'css/design-tokens.css' not in html
                    assert 'js/design-system.js' not in html
        finally:
            server.shutdown()
            thread.join()
    report = {'checks':results,'browser_errors':errors,'horizontal_overflow':[r for r in results if r['document'] > r['width']+2]}
    (output/('state-review.json' if state_review else 'browser-review.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(results),'errors':errors,'overflow':len(report['horizontal_overflow'])},ensure_ascii=False))


if __name__ == '__main__':
    run()
