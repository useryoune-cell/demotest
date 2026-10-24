import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.services.learning_analytics import learning_overview


class QuantityAnalytics(unittest.TestCase):
    def setUp(self):
        self.students = [
            {'username': 'a', 'name': 'A', 'teacher_username': 't1', 'school': 'S', 'class_name': '11A7'},
            {'username': 'b', 'name': 'B', 'teacher_username': 't1', 'school': 'S', 'class_name': '11A7'},
            {'username': 'c', 'name': 'C', 'teacher_username': 't1', 'school': 'S', 'class_name': '11A8'},
            {'username': 'other', 'teacher_username': 't2', 'school': 'S', 'class_name': '11A7'},
        ]
        self.now = datetime.now(timezone.utc)
        self.data = {}
        self.students_patch = patch('app.services.learning_analytics.list_students', return_value=self.students)
        self.storage_patch = patch('app.services.learning_analytics.load_json', side_effect=lambda name, default: self.data.get(name, default))
        self.students_patch.start(); self.storage_patch.start()
        self.addCleanup(self.students_patch.stop); self.addCleanup(self.storage_patch.stop)

    def event(self, identity, **extra):
        return dict(id=identity, module='nhiem-vu', action='submit', created_at=self.now.isoformat(), **extra)

    def test_scope_unique_students_duplicates_and_synthetic(self):
        self.data['activity.json'] = {
            'a': [self.event('1'), self.event('1'), self.event('2', synthetic=True)],
            'c': [self.event('3')], 'other': [self.event('4')],
        }
        stats = learning_overview('t1', class_name='11A7')['quantity']
        self.assertEqual((stats['total_students'], stats['active_students'], stats['inactive_students']), (2, 1, 1))
        self.assertEqual((stats['total'], stats['real'], stats['synthetic']), (2, 1, 1))
        self.assertEqual(sum(row['total'] for row in stats['days']), 2)

    def test_old_records_all_time_and_no_future_invalid_or_open_events(self):
        old = self.event('old'); old['created_at'] = (self.now - timedelta(days=60)).isoformat()
        future = self.event('future'); future['created_at'] = (self.now + timedelta(days=1)).isoformat()
        invalid = self.event('invalid'); invalid['created_at'] = 'bad'
        opening = self.event('open'); opening['action'] = 'start'
        self.data['activity.json'] = {'a': [old, future, invalid, opening]}
        self.assertEqual(learning_overview('t1')['quantity']['total'], 0)
        stats = learning_overview('t1', period='all')['quantity']
        self.assertEqual(stats['total'], 1)
        self.assertEqual(sum(row['total'] for row in stats['days']), 1)

    def test_review_ownership_zero_score_and_no_journal_double_count(self):
        row = {'student_username': 'a', 'teacher_username': 't1', 'submitted_at': self.now.isoformat(), 'teacher_score': ''}
        self.data['activity.json'] = {'a': [self.event('activity')]}
        self.data['assignments.json'] = {'submissions': [row, dict(row, teacher_score=0), dict(row, teacher_username='t2')]}
        self.data['teacher_content.json'] = {'argument_submissions': [dict(row, synthetic=True)]}
        stats = learning_overview('t1')['quantity']
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['reviews'], {'pending': 2, 'reviewed': 1, 'synthetic': 1})

    def test_local_day_and_naive_timestamp_supported(self):
        row = self.event('one')
        row['created_at'] = '2026-01-01T20:00:00'
        self.data['activity.json'] = {'a': [row]}
        stats = learning_overview('t1', period='all')['quantity']
        self.assertEqual(stats['days'][0]['date'], '2026-01-02')
        self.assertEqual(stats['days'][0]['total'], 1)

    def test_empty_denominators_and_calendar_window(self):
        stats = learning_overview('t1', school='unassigned')['quantity']
        self.assertEqual(stats['total_students'], 0)
        self.assertEqual(stats['total'], 0)
        self.assertEqual(len(stats['days']), 7)
        self.assertEqual((stats['module_max'], stats['day_max'], stats['review_max']), (1, 1, 1))


if __name__ == '__main__':
    unittest.main()
