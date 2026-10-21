import unittest
from unittest.mock import Mock, patch

from app.services.gemini_client import GeminiClient, GeminiClientError, GeminiKeyManager


class GeminiResilience(unittest.TestCase):
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
