import tempfile
import unittest
from copy import deepcopy

from app import app
from app.services.datatm_bank import question_bank, seed_datatm
from app.services.teacher_content_service import list_argument_packages, list_detective_cases, public_detective_case, upsert_detective_case
from app.services.compare_assignment_service import list_compare_packages
from app.services.assignment_service import list_tasks
from scripts.import_datatm import build


class DatatmImport(unittest.TestCase):
    def test_bundle_matches_word_documents(self):
        bank, duplicates = build()
        self.assertEqual(bank, question_bank())
        self.assertEqual(duplicates, 4)
        self.assertEqual({k: len(v) for k, v in bank.items()},
                         {'argument_packages': 23, 'detective_cases': 14, 'packages': 20, 'tasks': 8})

    def test_seed_keeps_edits_deletions_and_student_data(self):
        data = {'submissions': [{'id': 'keep'}]}
        self.assertTrue(seed_datatm(data, 'tasks'))
        data['tasks'][0]['title'] = 'Teacher edited'
        data['tasks'].pop()
        expected = deepcopy(data)
        self.assertFalse(seed_datatm(data, 'tasks'))
        self.assertEqual(data, expected)

    def test_services_expose_imported_questions_and_keep_solutions_private(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = app.config['DATA_DIR']
            app.config['DATA_DIR'] = directory
            try:
                with app.app_context():
                    for loader, count in [(list_argument_packages, 23), (list_detective_cases, 14),
                                          (list_compare_packages, 20), (list_tasks, 8)]:
                        rows = [r for r in loader() if r['id'].startswith('datatm-')]
                        self.assertEqual(len(rows), count)
                        self.assertTrue(all(r['active'] for r in rows))
                    case = next(c for c in list_detective_cases() if c.get('code') == 'TT01')
                    public = public_detective_case(case)
                    self.assertTrue({'evidence', 'rewrite', 'error_type', 'source_error_type'}.isdisjoint(public))
                    saved = upsert_detective_case(dict(case, case_id=case['id'], active='on'),
                                                  {'username': 'teacher01', 'name': 'Teacher'})
                    self.assertEqual(saved['code'], 'TT01')
                    task = next(t for t in list_tasks() if t['id'] == 'datatm-task-01')
                    self.assertIn('180–250', task['prompt'])
                    self.assertNotIn('Rubric', task['prompt'])
                    self.assertIn('10 điểm', task['rubric'])
                    client = app.test_client()
                    client.get('/app/modules/ban-do-lap-luan')
                    response = client.get('/api/modules/argument-map')
                    self.assertEqual(response.status_code, 200)
                    public_map = response.get_json()['argument_map']
                    self.assertNotIn('teacher_notes', public_map)
                    self.assertTrue(all('bucket' not in p for p in public_map['pieces']))
                    self.assertEqual(len(public_map['buckets']), 5)
            finally:
                app.config['DATA_DIR'] = previous
