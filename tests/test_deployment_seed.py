import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from app import create_app
from app.config import Config
from app.services.auth_service import verify_student
from app.services.deployment_seed import seed_runtime_data
from scripts.export_deployment_seed import export_bundle


class DeploymentSeed(unittest.TestCase):
    def test_startup_hash_login_and_preserve_live_work_without_duplicates(self):
        with tempfile.TemporaryDirectory(prefix='deploy-seed-test-') as temporary:
            root = Path(temporary)
            source = root / 'source'; source.mkdir()
            (source / 'auth.json').write_text(json.dumps({'teachers': [], 'students': [
                {'username': 'existing', 'password': 'bundled-old-password', 'active': True},
                {'username': 'new-learner', 'password': 'fixture-login-password', 'active': True}]}), encoding='utf-8')
            (source / 'activity.json').write_text(json.dumps({'existing': [{'id': 'old', 'created_at': '2026-10-01', 'score': 50}]}), encoding='utf-8')
            bundle = root / 'seed.zip'
            export_bundle(source, bundle)
            with zipfile.ZipFile(bundle) as archive:
                rows = json.loads(archive.read('auth.json'))['students']
                self.assertTrue(all('password' not in row and row['password_hash'] for row in rows))
            target = root / 'target'; target.mkdir()
            (target / 'auth.json').write_text(json.dumps({'teachers': [], 'students': [{'username': 'existing', 'password': 'new-live-password', 'active': True}]}), encoding='utf-8')
            (target / 'activity.json').write_text(json.dumps({'existing': [
                {'id': 'old', 'created_at': '2026-10-01', 'score': 95},
                {'id': 'live', 'created_at': '2026-10-24', 'score': 90}]}), encoding='utf-8')

            class SeedConfig(Config):
                TESTING = True
                DATA_DIR = str(target)
                SEED_DATA_BUNDLE = str(bundle)

            with patch.dict('os.environ', {'RENDER': 'true'}):
                app = create_app(SeedConfig)
            with app.app_context():
                self.assertIsNotNone(verify_student('new-learner', 'fixture-login-password'))
                self.assertIsNotNone(verify_student('existing', 'new-live-password'))
                self.assertIsNone(verify_student('existing', 'bundled-old-password'))
                self.assertFalse(seed_runtime_data(bundle))
            rows = json.loads((target / 'activity.json').read_text(encoding='utf-8'))['existing']
            self.assertEqual([r['id'] for r in rows], ['old', 'live'])
            self.assertEqual(rows[0]['score'], 95)
            self.assertEqual(len(list((target / 'backups').iterdir())), 1)

    def test_shipped_bundle_contains_classroom_data_without_plaintext_credentials(self):
        bundle = Path(__file__).resolve().parents[1] / 'app/data/deployment-seed.zip'
        with zipfile.ZipFile(bundle) as archive:
            self.assertTrue(all(name == 'manifest.json' or name.endswith('.json') for name in archive.namelist()))
            auth = json.loads(archive.read('auth.json'))
            self.assertEqual(sum(r.get('account_import_batch') == 'capnhat-simulation-v1' for r in auth['students']), 98)
            self.assertEqual(sum(r.get('account_import_batch') == 'capnhat-simulation-v1' for r in auth['teachers']), 4)
            self.assertTrue(all('password' not in row and row.get('password_hash') for kind in ('students', 'teachers') for row in auth[kind]))
            activity = json.loads(archive.read('activity.json'))
            rows = [row for group in activity.values() for row in group if row.get('import_batch') == 'capnhat-simulation-v1']
            self.assertEqual(len(rows), 3528)
            self.assertTrue(all(row['synthetic'] for row in rows))


if __name__ == '__main__':
    unittest.main()
