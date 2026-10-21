"""Seed bundled DATATM questions once; preserve teacher edits and deletions."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def question_bank():
    path = Path(__file__).resolve().parents[1] / 'data' / 'datatm_bank.json'
    return json.loads(path.read_text(encoding='utf-8'))


def seed_datatm(data, *collections):
    changed = False
    imported = data.setdefault('datatm_imported_ids', [])
    for collection in collections:
        rows = data.setdefault(collection, [])
        existing = {row['id'] for row in rows}
        for record in question_bank()[collection]:
            if record['id'] in imported:
                continue
            if record['id'] not in existing:
                rows.append(deepcopy(record))
                existing.add(record['id'])
            imported.append(record['id'])
            changed = True
    return changed
