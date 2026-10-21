"""Build the bundled question bank from DATATM Word files (stdlib only)."""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def paragraphs(path):
    with ZipFile(path) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
    return [text for p in document.findall('.//w:p', NS)
            if (text := ''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip())]


def groups(lines, pattern):
    result = []
    for line in lines:
        if re.match(pattern, line):
            result.append([])
        if result:
            result[-1].append(line)
    return result


def value(lines, prefix):
    return next((s.split(':', 1)[1].strip() for s in lines if s.startswith(prefix)), '')


def record(kind, number, filename, **fields):
    return dict(id=f'datatm-{kind}-{number:02}', teacher_username='teacher01',
                teacher_name='Giáo viên phản biện', active=True, created_at='datatm-v1',
                source_document=filename, **fields)


def build():
    bank = {'argument_packages': [], 'detective_cases': [], 'packages': [], 'tasks': []}
    duplicates = 0
    for path in sorted((ROOT / 'DATATM').glob('*.docx')):
        lines = paragraphs(path)
        if path.name.startswith('Bản đồ'):
            for number, block in enumerate(groups(lines, r'Tên gói(?:\s+\d+)?:'), 1):
                pieces = []
                for s in block:
                    if re.search(r'\|(claim|evidence|assumption|counter|conclusion)$', s):
                        text, bucket = s.rsplit('|', 1)
                        pieces.append(dict(id=f'p{len(pieces)+1}', text=text.strip(), bucket=bucket))
                assert len(pieces) == 5, (path, number, pieces)
                assert len({p['bucket'] for p in pieces}) == 5
                bank['argument_packages'].append(record('argument', number, path.name,
                    title=value(block, 'Tên gói'), question=value(block, 'Câu hỏi trung tâm:'),
                    source_text=value(block, 'Đoạn văn nguồn:'), pieces=pieces,
                    source_reference=value(block, 'Nguồn:'),
                    teacher_notes='\n'.join(s for s in block if s.startswith(('Đáp án', 'Luận điểm:', 'Bằng chứng:', 'Giả định:', 'Phản biện:', 'Kết luận:', 'Lưu ý:')))))
        elif path.name.startswith('Modun'):
            for block in groups(lines, r'Vấn đề \d+\.'):
                number = int(re.match(r'Vấn đề (\d+)', block[0])[1])
                choices = []
                for n, label in enumerate('ABC', 1):
                    text = value(block, f'Câu trả lời AI {label}:') or value(block, f'Lập luận {n} do AI tạo ra:')
                    assert text, (path, number, label)
                    choices.append(dict(label=label, text=text, trust='unclear'))
                key = value(block, 'Đáp án đúng:')
                match = re.match(r'(?:Lập luận\s+)?([123ABC])', key)
                assert match, (number, key)
                best = match[1]
                best = 'ABC'[int(best)-1] if best.isdigit() else best
                explanation = value(block, 'Giải thích đáp án đúng:')
                source = key.split('Nguồn kiểm chứng:', 1)[1].strip() if 'Nguồn kiểm chứng:' in key else ''
                notes = value(block, 'Điểm cần HS phát hiện:')
                bank['packages'].append(record('compare', number, path.name,
                    title=value(block, 'Tên gói bài:') or block[0].split('. ', 1)[1],
                    question=value(block, 'Câu hỏi học sinh cần đánh giá:') or block[0],
                    answers=choices, best=best,
                    explanation='\n'.join(s for s in (explanation, source, notes) if s)))
        elif path.name.startswith('Thám tử'):
            for block in groups(lines, r'Mã trạm:'):
                code = value(block, 'Mã trạm:')
                detail = value(block, 'Loại lỗi:')
                # Keep the full source taxonomy, while matching the existing learner choices.
                category = 'Khái quát hóa quá mức' if 'khái quát hóa quá mức' in detail.lower() else 'Dữ kiện sai'
                bank['detective_cases'].append(record('detective', int(code[2:]), path.name,
                    code=code, title=value(block, 'Tên lỗi:'), field=value(block, 'Lĩnh vực:'),
                    task=value(block, 'Nhiệm vụ học sinh cần làm:'), text=value(block, 'Câu trả lời AI có lỗi:'),
                    error_type=category, source_error_type=detail,
                    suspicious_text=value(block, 'Đoạn đáng nghi:').strip('“”"'),
                    evidence=value(block, 'Bằng chứng/nguồn kiểm chứng:'),
                    rewrite=value(block, 'Gợi ý viết lại đúng hơn:')))
        else:
            assert path.name.startswith('nhiệm vụ'), path
            seen = set()
            for block in groups(lines, r'Tên nhiệm vụ:'):
                title = value(block, 'Tên nhiệm vụ:')
                if title in seen:
                    duplicates += 1
                    continue
                seen.add(title)
                start = next(i for i, s in enumerate(block) if s.startswith('Đề bài học sinh cần làm:'))
                rubric_index = next(i for i, s in enumerate(block) if s.startswith('Rubric chấm điểm'))
                content = block[start:rubric_index]
                content[0] = content[0].split(':', 1)[1].strip()
                # Author's reference paragraph belongs with the teacher's rubric, not the question.
                reference = content.pop() if content[-1].startswith(('SGK ', 'Nội dung nhiệm vụ bám sát')) else ''
                rubric = block[rubric_index:rubric_index+5]
                assert len(rubric) == 5 and all(re.search(r'\d+ điểm', s) for s in rubric)
                bank['tasks'].append(record('task', len(seen), path.name,
                    title=title, prompt='\n'.join(content), rubric='\n'.join(rubric + [reference])))
    for collection, rows in bank.items():
        assert rows, collection
        for row in rows:
            required = {'argument_packages': ['title', 'question', 'source_text'],
                        'packages': ['title', 'question', 'explanation'],
                        'tasks': ['title', 'prompt', 'rubric'],
                        'detective_cases': ['code', 'title', 'field', 'task', 'text', 'error_type', 'suspicious_text', 'evidence', 'rewrite']}[collection]
            assert all(row[k] for k in required), row
    return bank, duplicates


if __name__ == '__main__':
    bank, duplicates = build()
    target = ROOT / 'app' / 'data' / 'datatm_bank.json'
    target.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print({key: len(rows) for key, rows in bank.items()}, 'duplicate tasks skipped:', duplicates)
