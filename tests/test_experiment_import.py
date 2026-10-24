import json
import math
import re
from pathlib import Path
import tempfile
import unittest

from app import app
from app.services.auth_service import verify_student, verify_teacher
from app.services.dashboard_service import student_profile
from scripts.import_experiment import BATCH, FILES, ROOT, apply_plan, build_plan


@unittest.skipUnless((ROOT / 'capnhat').is_dir(), 'Private source spreadsheets are only available locally.')
class ExperimentImport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='experiment-import-test-')
        self.directory = Path(self.temp.name)
        self.original_config = {k: app.config[k] for k in ('DATA_DIR', 'GEMINI_API_KEYS', 'TESTING')}
        app.config.update(DATA_DIR=self.temp.name, GEMINI_API_KEYS=[], TESTING=True)
        self.context = app.app_context()
        self.context.push()
        self.old_student = {'username': 'existing', 'password': 'keep-original', 'name': 'Existing', 'active': True}
        (self.directory / 'auth.json').write_text(json.dumps({'students': [self.old_student], 'teachers': [], 'reports': []}), encoding='utf-8')
        self.original_auth = (self.directory / 'auth.json').read_bytes()

    def tearDown(self):
        self.context.pop()
        app.config.update(self.original_config)
        self.temp.cleanup()

    def test_accounts_quotas_provenance_backup_and_no_duplicate_import(self):
        data, report = build_plan(self.directory, ROOT / 'capnhat')
        self.assertEqual(report['new_students'], 98)
        self.assertEqual(report['new_teachers'], 4)
        self.assertEqual((self.directory / 'auth.json').read_bytes(), self.original_auth)
        students = [r for r in data['auth.json']['students'] if r.get('account_import_batch') == BATCH]
        for student in students:
            expected_teacher = 'YT.PhamThiHang' if student['class_name'] == '11A7' else 'YT.LeNgocHa'
            self.assertEqual(student['teacher_username'], expected_teacher)
            activities = data['activity.json'][student['username']]
            self.assertTrue(all(a['synthetic'] for a in activities))
            for module, quota in report['quotas'].items():
                rows = [r for r in activities if r['module'] == module]
                if quota['available'] is not None:
                    self.assertEqual(quota['distinct_per_student'], math.ceil(quota['available'] * .2))
                    self.assertEqual(len(rows), quota['distinct_per_student'] * 2)
                    source_key = 'scenario_id' if module == 'prompt-phan-bien' else 'source_id'
                    self.assertEqual(len({r['payload'][source_key] for r in rows}), quota['distinct_per_student'])
                else:
                    self.assertEqual(len(rows), 1)
        for sub in data['assignments.json']['submissions']:
            self.assertTrue(180 <= len(sub['answer'].split()) <= 250, sub['task_id'])
            self.assertEqual(sub['teacher_score'], '')
            self.assertTrue(sub['synthetic'])
            self.assertEqual(sub['ai_meta']['model'], 'simulation')
        for sub in data['teacher_content.json']['argument_submissions']:
            self.assertEqual(sub['score'], round(sub['correct'] / sub['total'] * 100))
        backup = apply_plan(self.directory, data, report)
        self.assertEqual((backup / 'auth.json').read_bytes(), self.original_auth)
        self.assertEqual(next(s for s in data['auth.json']['students'] if s['username'] == 'existing'), self.old_student)
        password = re.search(r'\b([A-Za-z0-9]+@\d+)\b', (ROOT / 'capnhat/ghichu.txt').read_text(encoding='utf-8-sig')).group(1)
        self.assertIsNotNone(verify_teacher('YT.PhamThiHang', password))
        self.assertIsNotNone(verify_student(students[0]['username'], password))
        profile = student_profile(students[0]['username'])
        self.assertTrue(profile['has_synthetic_data'])
        self.assertEqual(len(profile['timeline']), 7)
        self.assertTrue(all(0 <= n <= 100 for n in profile['timeline']))
        client = app.test_client()
        with client.session_transaction() as session:
            session.update(role='student', student_username=students[0]['username'], student_name=students[0]['name'])
        response = client.get('/app/modules/ho-so-nang-luc')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dữ liệu mô phỏng', response.get_data(as_text=True))
        self.assertIn('Xem bài làm và nhận xét mô phỏng', response.get_data(as_text=True))
        expected_history = data['activity.json'][students[0]['username']]
        self.assertEqual(len(client.get('/api/modules/profile').json['activities']), len(expected_history))
        for teacher, other_teacher in [('YT.PhamThiHang', 'YT.LeNgocHa'), ('YT.LeNgocHa', 'YT.PhamThiHang')]:
            with client.session_transaction() as session:
                session.clear()
                session.update(role='teacher', teacher_username=teacher)
            response = client.get('/teacher/submissions')
            self.assertEqual(response.status_code, 200)
            own = next(s for s in students if s['teacher_username'] == teacher)
            other = next(s for s in students if s['teacher_username'] == other_teacher)
            self.assertIn(own['name'], response.get_data(as_text=True))
            self.assertNotIn(other['name'], response.get_data(as_text=True))
        before = {filename: (self.directory / filename).read_bytes() for filename in FILES}
        again, summary = build_plan(self.directory, ROOT / 'capnhat')
        self.assertEqual(summary['new_students'], 0)
        for filename in ('activity.json', 'reflections.json', 'assignments.json'):
            self.assertEqual(again[filename], json.loads(before[filename]))
        with self.assertRaises(ValueError):
            apply_plan(self.directory, again, summary)
        self.assertEqual(before, {filename: (self.directory / filename).read_bytes() for filename in FILES})

    def test_changed_runtime_aborts_before_writing(self):
        data, report = build_plan(self.directory, ROOT / 'capnhat')
        (self.directory / 'activity.json').write_text('{"existing": []}', encoding='utf-8')
        with self.assertRaises(ValueError):
            apply_plan(self.directory, data, report)
        self.assertEqual((self.directory / 'auth.json').read_bytes(), self.original_auth)
        self.assertFalse((self.directory / 'backups').exists())


if __name__ == '__main__':
    unittest.main()
