"""Export runtime JSON for Render; credentials are hashed, .env is never read."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from app.services.deployment_seed import SEED_FILES
from app.services.storage import data_dir
from werkzeug.security import generate_password_hash


def export_bundle(source, destination):
    records = {}
    for name in SEED_FILES:
        path = source / name
        if not path.exists():
            continue
        value = json.loads(path.read_text(encoding='utf-8-sig'))
        if name == 'auth.json':
            for role in ('students', 'teachers'):
                for account in value.get(role, []):
                    password = account.pop('password', None)
                    if password is not None and not account.get('password_hash'):
                        account['password_hash'] = generate_password_hash(password)
        if name == 'experiment-import.json':
            value.pop('backup_directory', None)
            value.pop('runtime_before_sha256', None)
        records[name] = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    manifest = {'version': 'classroom-seed-2026-10-24', 'exported_at': datetime.now(timezone.utc).isoformat(),
                'contains_synthetic_learning_data': True,
                'files': {name: hashlib.sha256(raw).hexdigest() for name, raw in records.items()}}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
        for name, raw in records.items():
            archive.writestr(name, raw)
    return {'files': len(records), 'archive_bytes': destination.stat().st_size}


if __name__ == '__main__':
    with app.app_context():
        result = export_bundle(Path(data_dir()), Path(__file__).resolve().parents[1] / 'app/data/deployment-seed.zip')
        print(json.dumps(result))
