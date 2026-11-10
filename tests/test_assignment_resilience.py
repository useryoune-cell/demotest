import unittest
from unittest.mock import Mock, patch

from app.services.gemini_client import GeminiClient, GeminiClientError, GeminiKeyManager


class GeminiResilience(unittest.TestCase):
    def test_fast_thinking_is_sent_only_to_gemini_3_flash(self):
        response = Mock(status_code=200, ok=True)
        response.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'hint'}]}}]}
        for model, thinking_level, expected in [('gemini-3.5-flash', 'minimal', {'thinkingLevel': 'minimal'}),
                ('gemini-3.5-flash', 'high', {'thinkingLevel': 'high'}),
                ('gemini-3.5-flash', '', None), ('gemini-2.5-flash', 'minimal', None)]:
            with self.subTest(model=model, thinking_level=thinking_level):
                client = GeminiClient(GeminiKeyManager(['test']), model, thinking_level=thinking_level)
                with patch('app.services.gemini_client.requests.post', return_value=response) as request:
                    client.generate_text('question')
                generation = request.call_args.kwargs['json']['generationConfig']
                self.assertEqual(generation.get('thinkingConfig'), expected)

    def test_assignment_chat_distinguishes_provider_reply_from_fallback(self):
        import tempfile
        from types import SimpleNamespace
        from app import create_app
        from app.services.auth_service import create_student
        from app.services.assignment_service import list_tasks

        with tempfile.TemporaryDirectory() as directory:
            app = create_app()
            app.config.update(TESTING=True, DATA_DIR=directory, GEMINI_API_KEYS=['test'])
            with app.app_context():
                create_student('diagnostic', 'test-password', 'Test', 'School', '10A', 'teacher01')
                task = list_tasks(active_only=True)[0]
            client = app.test_client()
            with client.session_transaction() as session:
                session.update(role='student', student_username='diagnostic')
            client.post('/api/modules/assignments/consent', json={'task_id': task['id']})
            attempt = client.post('/api/modules/assignments/start', json={'task_id': task['id']}).json['attempt']
            provider = Mock()
            provider.generate_text.side_effect = [GeminiClientError('ReadTimeout'),
                SimpleNamespace(text='Em hãy kiểm chứng bằng chứng.', model='test-model', key_index=0, attempts=1)]
            with patch('app.routes.GeminiClient.from_app_config', return_value=provider):
                for available in (False, True):
                    response = client.post('/api/modules/assignments/chat', json={
                        'task_id': task['id'], 'attempt_id': attempt['id'], 'message': 'Hãy giải thích thêm'})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json['ai_available'], available)
                    self.assertTrue(response.json['answer'])

    def test_default_budget_stops_retrying_other_keys(self):
        client = GeminiClient(GeminiKeyManager(['test-a', 'test-b']), 'test-model')
        with patch('app.services.gemini_client.time.monotonic', side_effect=[0, 0, 36]), \
             patch.object(client, '_request_with_key', side_effect=GeminiClientError('timeout')) as request:
            with self.assertRaises(GeminiClientError):
                client.generate_text('question')
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.args[2], 35)

    def test_network_error_does_not_expose_key_in_exception_or_status(self):
        import requests
        client = GeminiClient(GeminiKeyManager(['private-test-secret']), 'test-model')
        with patch('app.services.gemini_client.requests.post', side_effect=requests.Timeout('url?key=private-test-secret')):
            with self.assertRaises(GeminiClientError) as error:
                client.generate_text('question')
        self.assertNotIn('private-test-secret', str(error.exception))
        self.assertNotIn('private-test-secret', client.key_manager.status()[0]['last_error'])

    def test_retries_share_time_budget(self):
        client = GeminiClient(GeminiKeyManager(['test-a', 'test-b']), 'test-model')
        with patch('app.services.gemini_client.time.monotonic', side_effect=[0, 0, 18.1]), \
             patch.object(client, '_request_with_key', side_effect=GeminiClientError('timeout')) as request:
            with self.assertRaises(GeminiClientError):
                client.generate_text('question', deadline_seconds=18)
        self.assertEqual(request.call_count, 1)

    def test_invalid_json_becomes_handled_provider_error(self):
        client = GeminiClient(GeminiKeyManager(['test']), 'test-model')
        response = Mock(status_code=200, ok=True)
        response.json.side_effect = ValueError('not JSON')
        with patch('app.services.gemini_client.requests.post', return_value=response):
            with self.assertRaises(GeminiClientError):
                client.generate_text('question', deadline_seconds=18)

    def test_network_timeouts_fit_remaining_budget(self):
        client = GeminiClient(GeminiKeyManager(['test']), 'test-model')
        response = Mock(status_code=200, ok=True)
        response.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'hint'}]}}]}
        with patch('app.services.gemini_client.requests.post', return_value=response) as request:
            result = client.generate_text('question', deadline_seconds=18)
        self.assertEqual(result.text, 'hint')
        self.assertLessEqual(sum(request.call_args.kwargs['timeout']), 18)
