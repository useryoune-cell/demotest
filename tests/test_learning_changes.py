import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import app, create_app
from app.services.auth_service import create_student, create_teacher, get_student, update_student_class
from app.services.storage import load_json, save_json
from app.services.teacher_content_service import get_argument_package, get_detective_case, score_argument_package, score_detective_case
from app.services.compare_assignment_service import evaluate_compare, get_compare_package
from app.services.assignment_service import get_task, fallback_assignment_chat
from app.services.learning_feedback import criterion, review_text
from app.services.learning_analytics import SELF_ASSESSMENT, save_self_assessment, save_chatbot_rating, learning_overview


class LearningChanges(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='critical-thinking-tests-')
        app.config.update(TESTING=True, DATA_DIR=self.directory.name, GEMINI_API_KEYS=[])
        self.context = app.app_context(); self.context.push()
        self.client = app.test_client()
        self.student = create_student('learner', 'test-password', 'Học sinh', 'Trường A', '10A', 'teacher01')
        self.login_student()

    def tearDown(self):
        self.context.pop(); self.directory.cleanup()

    def login_student(self, username='learner'):
        with self.client.session_transaction() as session:
            session.clear(); session.update(role='student', student_username=username, student_name='Học sinh')

    def login_teacher(self, username='teacher01'):
        with self.client.session_transaction() as session:
            session.clear(); session.update(role='teacher', teacher_username=username, teacher_name='Giáo viên')

    def test_login_hides_role_picker_and_has_logout(self):
        text = self.client.get('/app').get_data(as_text=True)
        self.assertNotIn('aria-label="Chọn vai trò đăng nhập"', text)
        self.assertIn('Đăng xuất', text)
        self.assertIn('Học sinh', text)

    def test_registration_requires_class(self):
        response = self.client.post('/student/register', data={'username': 'missing', 'password': 'pw'})
        self.assertIn('Cần nhập trường, lớp', response.get_data(as_text=True))
        self.assertIsNone(get_student('missing'))

    def test_registration_persists_class(self):
        response = self.client.post('/student/register', data={'username':'new','password':'pw','name':'New','school':'Trường B','class_name':'9A','teacher_username':'teacher01'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_student('new')['class_name'], '9A')

    def test_map_levels_and_no_answer_keys_in_result(self):
        package = get_argument_package(active_only=True)
        for n, expected in [(0,'Cần xem lại'),(2,'Cần xem lại'),(3,'Đang hình thành'),(4,'Đạt'),(5,'Thành thạo')]:
            result = score_argument_package(package['id'], {p['id']: p['bucket'] for p in package['pieces'][:n]})
            self.assertEqual(result['score'], n*20)
            self.assertEqual(result['level'], expected)
            self.assertTrue(all('expected' not in d for d in result['details']))
            self.assertEqual(bool(result['reflection']), n == 5)

    def test_long_nonsense_does_not_get_written_points(self):
        case = get_detective_case('A', active_only=True)
        result = score_detective_case('A', case['suspicious_text'], case['error_type'], 'abc '*1000, 'abc '*1000, 'abc '*1000)
        self.assertEqual(result['score'], 40)
        self.assertTrue(result['provisional'])
        self.assertEqual(len(result['rubric']), 5)
        self.assertNotIn('expected', result)
        self.assertTrue(all(r['status'] == 'Chưa đủ bằng chứng' for r in result['rubric'][2:]))

    def test_tiny_substring_not_accepted_as_suspicious(self):
        result = score_detective_case('A', '1', 'other', '', '', '')
        self.assertEqual(result['rubric'][0]['score'], 0)

    def test_solution_only_after_submission_and_for_owner(self):
        case = get_detective_case('A', active_only=True)
        payload = dict(code='A', suspicious_text=case['suspicious_text'], error_type=case['error_type'], explanation='Lý do', evidence='Nguồn', rewrite='Câu sửa')
        response = self.client.post('/api/modules/detective/score', json=payload)
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertNotIn('expected', result)
        url = '/api/modules/detective/solution/' + result['submission_id']
        answer = self.client.get(url).get_json()
        self.assertEqual(answer['evidence'], case['evidence'])
        create_student('other', 'pw', 'Other')
        self.login_student('other')
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_ai_json_validated_and_content_returned(self):
        app.config['GEMINI_API_KEYS'] = ['test-only']
        data = {'rubric':[{'key':'reason','score':12,'status':'Chưa đúng','feedback':'Kết luận của em vượt quá ví dụ đã nêu.'}], 'feedback':'Cần xét trường hợp ngược lại.', 'reflection':'Điều gì khiến em đổi ý?'}
        fake = SimpleNamespace(generate_text=lambda prompt: SimpleNamespace(text=json.dumps(data)))
        with patch('app.services.learning_feedback.GeminiClient.from_app_config', return_value=fake):
            result = review_text('context', {'answer':'text'}, [criterion('reason','Lý lẽ',20,'hint')])
        self.assertTrue(result['ai_available'])
        self.assertEqual(result['rubric'][0]['score'], 12)

    def test_invalid_ai_scores_leave_review_pending(self):
        app.config['GEMINI_API_KEYS'] = ['test-only']
        for points in [-1, 999, True, float('nan'), '20']:
            data = {'rubric':[{'key':'reason','score':points,'status':'Đúng','feedback':'text'}], 'feedback':'text','reflection':'text'}
            fake = SimpleNamespace(generate_text=lambda prompt: SimpleNamespace(text=json.dumps(data)))
            with patch('app.services.learning_feedback.GeminiClient.from_app_config', return_value=fake):
                result = review_text('context', {}, [criterion('reason','Lý lẽ',20,'hint')])
            self.assertFalse(result['ai_available'])
            self.assertEqual(result['rubric'][0]['score'], 0)

    def test_compare_correctness_and_no_length_points(self):
        package = get_compare_package()
        result = evaluate_compare(package, package['best'], 'abc '*1000, 'abc '*1000)
        self.assertTrue(result['correct'])
        self.assertEqual(result['score'], 30)
        self.assertTrue(result['provisional'])

    def test_provisional_grade_not_added_to_profile(self):
        package = get_compare_package()
        self.client.post('/api/modules/compare/score', json={'package_id':package['id'],'selected':package['best'],'criteria':'abc '*30,'synthesis':'abc '*30})
        activities = load_json('activity.json', {})['learner']
        self.assertIsNone(activities[-1]['score'])

    def test_missing_content_id_does_not_grade_first_item(self):
        self.assertIsNone(get_compare_package('does-not-exist'))
        self.assertIsNone(get_argument_package('does-not-exist'))
        self.assertIsNone(get_task('does-not-exist'))

    def test_analytics_scoped_and_latest_response_counted(self):
        create_teacher('second', 'pw', 'Second', '')
        other = create_student('other', 'pw', 'Other', 'Trường A', '10A', 'second')
        for score in (1, 5):
            save_self_assessment(self.student, {q['key']:str(score) for q in SELF_ASSESSMENT})
        save_self_assessment(other, {q['key']:'1' for q in SELF_ASSESSMENT})
        save_chatbot_rating(self.student, 'nhiem-vu', '2', '')
        save_chatbot_rating(self.student, 'nhiem-vu', '5', '')
        data = learning_overview('teacher01')
        self.assertEqual(data['classes'][0]['count'], 1)
        self.assertEqual(data['classes'][0]['skills'][0]['mean'], 5)
        self.assertEqual(data['rating_count'], 1)
        self.assertEqual(data['rating_mean'], 5)
        self.assertEqual(learning_overview('teacher01', school='Unknown')['classes'], [])

    def test_old_survey_outside_period_and_invalid_scale(self):
        row = save_self_assessment(self.student, {q['key']:'3' for q in SELF_ASSESSMENT})
        data = load_json('learning_surveys.json', {})
        data['self_assessments'][0]['created_at'] = '2000-01-01T00:00:00+00:00'
        save_json('learning_surveys.json', data)
        self.assertFalse(learning_overview('teacher01')['classes'])
        with self.assertRaises(ValueError):
            save_self_assessment(self.student, {q['key']:'6' for q in SELF_ASSESSMENT})

    def test_teacher_cannot_delete_other_teachers_package(self):
        package = get_compare_package()
        create_teacher('second', 'pw', 'Second', '')
        self.login_teacher('second')
        response = self.client.post('/teacher/compare/packages/'+package['id']+'/delete')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(get_compare_package(package['id']))
        self.assertNotIn(package['title'], self.client.get('/teacher/compare').get_data(as_text=True))

    def test_assignment_context_has_current_question_and_ownership(self):
        task = get_task(active_only=True)
        self.client.post('/api/modules/assignments/consent', json={'task_id':task['id']})
        response = self.client.post('/api/modules/assignments/start', json={'task_id':task['id']})
        attempt_id = response.get_json()['attempt']['id']
        app.config['GEMINI_API_KEYS'] = ['test-only']
        captured = []
        fake = SimpleNamespace(generate_text=lambda prompt, **kwargs: (captured.append(prompt) or SimpleNamespace(text='Gợi ý',model='mock',key_index=0,attempts=1)))
        with patch('app.routes.GeminiClient.from_app_config', return_value=fake):
            response = self.client.post('/api/modules/assignments/chat', json={'task_id':task['id'],'attempt_id':attempt_id,'message':'Kiểm chứng nguồn như thế nào?','messages':[]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Kiểm chứng nguồn như thế nào?', captured[0])
        create_student('other', 'pw', 'Other')
        self.login_student('other')
        response = self.client.post('/api/modules/assignments/chat', json={'task_id':task['id'],'attempt_id':attempt_id,'message':'Question'})
        self.assertEqual(response.status_code, 404)

    def test_chat_fallback_varies_with_question(self):
        task = get_task()
        self.assertNotEqual(fallback_assignment_chat(task, 'nguồn'), fallback_assignment_chat(task, 'phản biện'))

    def test_startup_preserves_existing_student_data(self):
        save_json('activity.json', {'learner':[{'action':'keep'}]})
        class Config:
            TESTING = True
            SECRET_KEY = 'test'
            DATA_DIR = self.directory.name
        create_app(Config)
        self.assertEqual(load_json('activity.json', {})['learner'][0]['action'], 'keep')

    def test_main_pages_render(self):
        for url in ['/app','/app/learning-profile','/app/modules/so-sanh-ba-cau-tra-loi','/app/modules/ban-do-lap-luan','/app/modules/tham-tu-ai?field=kiem-chung-nguon-ai','/app/modules/nhiem-vu','/app/modules/prompt-phan-bien']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.login_teacher()
        for page in ['overview','students','compare','detective','argument','assignments','submissions','reports']:
            self.assertEqual(self.client.get('/teacher/'+page).status_code, 200, page)

    def test_map_api_hides_answers_and_rejects_unknown_id(self):
        data = self.client.get('/api/modules/argument-map').get_json()
        self.assertTrue(all('bucket' not in p for p in data['argument_map']['pieces']))
        response = self.client.post('/api/modules/argument-map/score', json={'map_id':'missing','placements':{}})
        self.assertEqual(response.status_code, 404)

    def test_debate_pending_does_not_change_rank_or_fill_cookie(self):
        response = self.client.post('/api/modules/debate/judge', json={'topic_index':0,'player_argument':'Em cần kiểm tra bằng chứng trước khi đưa ra kết luận.'})
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result['winner'], 'pending')
        self.assertEqual(result['rank_delta'], 0)
        self.assertEqual(self.client.get(result['result_url']).status_code, 200)
        with self.client.session_transaction() as session:
            self.assertNotIn('last_debate_result', session)

    def test_survey_concurrent_writes_preserve_all_responses(self):
        from concurrent.futures import ThreadPoolExecutor
        def write(n):
            with app.app_context():
                save_chatbot_rating(self.student, 'nhiem-vu', str(n % 5 + 1), str(n))
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(write, range(20)))
        self.assertEqual(len(load_json('learning_surveys.json', {})['chatbot_ratings']), 20)


if __name__ == '__main__':
    unittest.main()
