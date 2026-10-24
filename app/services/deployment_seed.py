"""Add bundled accounts and learning records, without replacing live data."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

from app.services.storage import data_dir, save_json

SEED_FILES = ('auth.json', 'activity.json', 'assignments.json', 'teacher_content.json',
              'compare_assignments.json', 'reflections.json', 'debate_config.json',
              'experiment-import.json', 'learning_surveys.json', 'debate_results.json')


def _identity(value):
    if isinstance(value, dict):
        for key in ('username', 'id'):
            if value.get(key):
                return key, str(value[key])
    return 'value', json.dumps(value, sort_keys=True, ensure_ascii=False)


def merge_missing(current, seed):
    """Existing credentials, grades and answers win, including nested records."""
    if isinstance(current, dict) and isinstance(seed, dict):
        result = deepcopy(current)
        for key, value in seed.items():
            result[key] = merge_missing(result[key], value) if key in result else deepcopy(value)
        return result
    if isinstance(current, list) and isinstance(seed, list):
        result = deepcopy(current)
        seen = {_identity(value) for value in result}
        for value in seed:
            key = _identity(value)
            if key not in seen:
                result.append(deepcopy(value))
                seen.add(key)
        if result and all(isinstance(r, dict) and ('created_at' in r or 'submitted_at' in r) for r in result):
            result.sort(key=lambda r: r.get('submitted_at') or r.get('created_at', ''))
        return result
    return deepcopy(current)


def seed_runtime_data(bundle):
    bundle = Path(bundle)
    if not bundle.is_file():
        raise RuntimeError(f'Deployment seed bundle missing: {bundle.name}')
    directory = Path(data_dir())
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    marker = directory / 'deployment-seed-state.json'
    if marker.exists() and json.loads(marker.read_text(encoding='utf-8')).get('sha256') == digest:
        return False
    planned = {}
    originals = {}
    with zipfile.ZipFile(bundle) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        for name, expected in manifest['files'].items():
            if name not in SEED_FILES:
                raise ValueError(f'Unexpected seed file: {name}')
            raw = archive.read(name)
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError(f'Seed checksum mismatch: {name}')
            seed = json.loads(raw)
            path = directory / name
            originals[name] = path.read_bytes() if path.exists() else None
            if originals[name] is not None:
                current = json.loads(originals[name])
                # Settings and import metadata are initial values, not user records.
                planned[name] = current if name in {'debate_config.json', 'experiment-import.json'} else merge_missing(current, seed)
            else:
                planned[name] = seed
    originals[marker.name] = marker.read_bytes() if marker.exists() else None
    backup = directory / 'backups' / ('deployment-seed-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
    backup.mkdir(parents=True, exist_ok=False)
    for name, raw in originals.items():
        if raw is not None:
            (backup / name).write_bytes(raw)
    try:
        for name, value in planned.items():
            save_json(name, value)
        save_json(marker.name, {'sha256': digest, 'version': manifest['version'],
                               'applied_at': datetime.now(timezone.utc).isoformat(),
                               'backup_directory': str(backup)})
    except BaseException:
        for name, raw in originals.items():
            path = directory / name
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(raw)
        raise
    return True
