import json
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app import create_app
from app.services.prompt_service import PROMPT_SCENARIOS, RUBRIC


class PromptWorkshop(unittest.TestCase):
    def test_selected_scenario_and_four_criteria_reach_ai(self):
        with tempfile.TemporaryDirectory(prefix='prompt-workshop-') as directory:
            app = create_app()
            app.config.update(TESTING=True, DATA_DIR=directory, GEMINI_API_KEYS=['test-key'])
            client = app.test_client()
            with client.session_transaction() as session:
                session.update(role='student', student_username='student01')
            prompts = []
            fixture = {'rubric': [{'key': r['key'], 'score': 25, 'status': 'Đúng', 'feedback': 'Có yêu cầu cụ thể.'} for r in RUBRIC],
                       'feedback': 'Prompt yêu cầu kiểm chứng và điều chỉnh kết luận.', 'reflection': 'Em sẽ đối chiếu nguồn nào?'}

            def generate(prompt, **kwargs):
                prompts.append(prompt)
                return SimpleNamespace(text=json.dumps(fixture))

            with patch('app.services.learning_feedback.GeminiClient.from_app_config', return_value=SimpleNamespace(generate_text=generate)):
                response = client.post('/api/modules/prompt/score', json={'prompt': 'Verify evidence and revise the conclusion.', 'scenario_id': 'balanced-ai-policy'})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['ai_available'])
            self.assertEqual(len(response.json['rubric']), 4)
            self.assertEqual(response.json['score'], 100)
            self.assertIn(PROMPT_SCENARIOS[1]['task'], prompts[0])
            response = client.post('/api/modules/prompt/score', json={'prompt': 'Verify evidence and revise the conclusion.', 'scenario_id': 'missing'})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
