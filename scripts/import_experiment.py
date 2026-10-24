"""Import supplied XLSX accounts and explicitly synthetic learning records.

Defaults to preview. --apply backs up all affected runtime files before writing.
No API calls; grades, dialogue and dates are simulated, never teacher decisions.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from app.services.storage import data_dir, save_json
from app.services.assignment_service import DEFAULT_ASSIGNMENT_DATA, DEMO_EXTRA_TASK
from app.services.compare_assignment_service import DEFAULT_COMPARE_DATA, DEMO_EXTRA_PACKAGE
from app.services.teacher_content_service import DEFAULT_ARGUMENT_PACKAGES, DEFAULT_DETECTIVE_CASES

BATCH = 'capnhat-simulation-v1'
ROOT = Path(__file__).resolve().parents[1]
FILES = ('auth.json', 'activity.json', 'assignments.json',
         'teacher_content.json', 'compare_assignments.json', 'reflections.json')
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
LABEL = '[MÔ PHỎNG] '
SOURCE = 'SGK Lịch sử 11 – Kết nối tri thức; nội dung ngân hàng DATATM đã nạp trong dự án'


def spreadsheet(path):
    """Read first sheet, respecting sparse cells, shared and inline strings."""
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(n.itertext()) for n in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rows = []
        for row in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('.//s:row', NS):
            values = {}
            for cell in row:
                col = re.sub(r'\d+', '', cell.attrib['r'])
                v = cell.find('s:v', NS)
                value = v.text if v is not None else ''.join(cell.itertext())
                values[col] = strings[int(value)] if cell.get('t') == 's' else (value or '')
            if any(values.values()):
                rows.append(values)
        headers = rows[0]
        return [{headers[col]: row.get(col, '').strip() for col in headers} for row in rows[1:]]


def identifier(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, ':'.join((BATCH, *map(str, parts)))))


def stamp(**extra):
    return {'synthetic': True, 'import_batch': BATCH, 'provenance': 'generated_simulation', **extra}


def read_data(directory):
    # Fail rather than replace a malformed runtime file with empty defaults.
    result = {}
    for filename in FILES:
        path = directory / filename
        result[filename] = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    return result


def add_unique(rows, entry):
    if not any(row.get('id') == entry['id'] for row in rows):
        rows.append(entry)


def feedback(score, detail, revision):
    labels = [('claim', 'Luận điểm'), ('evidence', 'Bằng chứng'),
              ('reasoning', 'Suy luận'), ('counter', 'Phản biện'), ('revision', 'Tự điều chỉnh')]
    points = [score // 5 + (i < score % 5) for i in range(5)]
    return {
        **stamp(), 'score': score, 'ai_available': False, 'provisional': False,
        'assessment_source': 'simulation', 'hint': LABEL + 'Đối chiếu lại luận điểm với căn cứ trong SGK.',
        'feedback': LABEL + (f'Bài đã bổ sung đối chiếu: {detail[:230]}. ' if revision else
                             f'Bài mới nêu được ý chính: {detail[:180]}. ') +
                    'Cần chỉ rõ căn cứ nào hỗ trợ kết luận và giới hạn của cách giải thích.',
        'reflection': 'Nếu bỏ một bằng chứng quan trọng, kết luận của em cần thay đổi như thế nào?',
        'rubric': [{'key': key, 'label': label, 'max': 20, 'score': points[i],
                    'status': 'Đạt' if points[i] >= 14 else 'Cần bổ sung',
                    'feedback': LABEL + ('Đã xét căn cứ và giới hạn; hãy nêu rõ phần còn chưa chắc.'
                                        if revision else 'Cần nối chi tiết trong bài với căn cứ SGK, tránh khẳng định quá mức.')}
                   for i, (key, label) in enumerate(labels)],
    }


def task_facts(task):
    rubric = task['rubric']
    markers = ('Nội dung nhiệm vụ bám sát', 'SGK cho thấy', 'SGK nêu', 'SGK xác định')
    locations = [rubric.index(m) for m in markers if m in rubric]
    return rubric[min(locations):] if locations else rubric


def essay(task, revision, variant):
    facts = task_facts(task)
    openings = [
        'Theo em, cần xem xét nhận định trong đề bằng các dẫn chứng của bài học, thay vì chấp nhận chỉ vì AI diễn đạt tự tin.',
        'Em cho rằng đánh giá một vấn đề lịch sử cần đặt sự kiện trong bối cảnh và phân biệt dữ kiện với cách giải thích dữ kiện đó.',
        'Với vấn đề được nêu, em muốn đối chiếu tài liệu trước khi kết luận, vì một nhận định ngắn có thể bỏ qua các điều kiện quan trọng.',
    ]
    body = (openings[variant % len(openings)] + ' ' + facts +
            ' Chi tiết này cho thấy kết luận cần dựa vào nội dung cụ thể, không chỉ dựa vào một cụm từ khái quát. '
            'Em cần giải thích mối liên hệ giữa bằng chứng và quan điểm mình lựa chọn, đồng thời tránh coi một yếu tố là lời giải duy nhất. ')
    if revision:
        body += ('Sau khi đối chiếu, em điều chỉnh cách viết: cần xét cả mặt được khẳng định và giới hạn của nhận định. '
                 'Một ý kiến khác chỉ có sức thuyết phục khi đưa ra dẫn chứng phù hợp với bối cảnh. '
                 'Vì vậy, em kết luận trong phạm vi tài liệu đã học và sẽ kiểm tra thêm nếu có bằng chứng ngược lại. ')
    else:
        body += ('Ở lần viết đầu, em mới nêu ý chính và chưa phân tích đầy đủ một cách nhìn khác. '
                 'Em còn cần bổ sung dẫn chứng cụ thể trước khi khẳng định mức độ đúng của nhận định. ')
    while len(body.split()) < 185:
        body += 'Em sẽ ghi rõ nguồn của dữ kiện và kiểm tra xem bằng chứng có thực sự hỗ trợ kết luận hay không. '
    if len(body.split()) > 245:
        # Keep the source facts intact; long factual anchors have no generic padding.
        body = openings[variant % len(openings)] + ' ' + facts
        if revision:
            body += ' Em bổ sung góc nhìn khác và giới hạn: kết luận chỉ phù hợp trong bối cảnh, phạm vi bằng chứng đã đối chiếu.'
        while len(body.split()) < 185:
            body += ' Em cần đối chiếu từng dữ kiện với bài học, giải thích quan hệ giữa bằng chứng và kết luận, tránh chỉ kể lại sự kiện.'
    return body.strip()


def build_plan(directory, source_dir):
    data = read_data(directory)
    teacher_file = next(source_dir.glob('ds tài khoản gv*.xlsx'))
    student_file = next(source_dir.glob('ds tài khoản hs*.xlsx'))
    teachers = spreadsheet(teacher_file)
    students = spreadsheet(student_file)
    note = (source_dir / 'ghichu.txt').read_text(encoding='utf-8-sig')
    match = re.search(r'\b([A-Za-z0-9]+@\d+)\b', note)
    if not match:
        raise ValueError('Không tìm thấy mật khẩu chung trong ghichu.txt.')
    password = match.group(1)
    if len({r['Tài khoản'] for r in students}) != len(students):
        raise ValueError('Danh sách HS có tài khoản trùng.')
    classes = list(dict.fromkeys((r['Trường'], r['Lớp học']) for r in students))
    if len(classes) > len(teachers):
        raise ValueError('Số lớp vượt số GV; cần cấu hình phân công.')
    assignment = {room: teachers[i] for i, room in enumerate(classes)}
    now = datetime.now(timezone.utc).isoformat()
    auth = data['auth.json']
    auth.setdefault('teachers', []); auth.setdefault('students', []); auth.setdefault('reports', [])
    counts = {'new_teachers': 0, 'new_students': 0}
    for role, rows in [('teachers', teachers), ('students', students)]:
        for row in rows:
            username = row['Tài khoản']
            existing = next((r for r in auth[role] if r['username'] == username), None)
            if existing:
                if existing.get('account_import_batch') != BATCH:
                    raise ValueError(f'Tài khoản đã có ngoài đợt nạp: {username}')
                continue
            account = {'username': username, 'password': password, 'name': row['Họ tên'],
                       'school': row['Trường'], 'active': True, 'created_at': now,
                       'account_import_batch': BATCH, 'source_file': teacher_file.name if role == 'teachers' else student_file.name}
            if role == 'students':
                account.update(class_name=row['Lớp học'], avatar_filename='',
                               teacher_username=assignment[(row['Trường'], row['Lớp học'])]['Tài khoản'])
            else:
                account.update(subject=row['Môn'], email='')
            auth[role].append(account)
            counts['new_' + role] += 1

    bank = json.loads((ROOT / 'app/data/datatm_bank.json').read_text(encoding='utf-8'))
    # Count built-in exercises too, even on a fresh runtime before first page load.
    for filename, key, defaults in [
        ('assignments.json', 'tasks', [*DEFAULT_ASSIGNMENT_DATA['tasks'], DEMO_EXTRA_TASK]),
        ('compare_assignments.json', 'packages', [*DEFAULT_COMPARE_DATA['packages'], DEMO_EXTRA_PACKAGE]),
        ('teacher_content.json', 'argument_packages', DEFAULT_ARGUMENT_PACKAGES),
        ('teacher_content.json', 'detective_cases', DEFAULT_DETECTIVE_CASES),
    ]:
        for record in defaults:
            add_unique(data[filename].setdefault(key, []), deepcopy(record))
    # Source content remains shared; the class teacher is the reviewer of these imports.
    configs = [
        ('nhiem-vu', 'assignments.json', 'tasks', 'submissions'),
        ('tham-tu-ai', 'teacher_content.json', 'detective_cases', 'detective_submissions'),
        ('so-sanh-ba-cau-tra-loi', 'compare_assignments.json', 'packages', 'submissions'),
        ('ban-do-lap-luan', 'teacher_content.json', 'argument_packages', 'argument_submissions'),
    ]
    quotas = {}
    pools = {}
    for module, filename, key, _ in configs:
        db = data[filename]
        existing = db.setdefault(key, [])
        for item in bank[key]:
            add_unique(existing, deepcopy(item))
        active = [r for r in existing if r.get('active', True)]
        pool = [r for r in active if r['id'] in {x['id'] for x in bank[key]}]
        quotas[module] = {'available': len(active), 'distinct_per_student': math.ceil(len(active) * .2),
                          'rounds_per_exercise': 2}
        if quotas[module]['distinct_per_student'] > len(pool):
            raise ValueError('Không đủ bài SGK để đạt tỷ lệ đã chọn.')
        pools[module] = pool
    quotas['prompt-phan-bien'] = {'available': 2, 'distinct_per_student': 1, 'rounds_per_exercise': 2}
    # Socratic and journals have no finite question bank: use one source-grounded
    # six-stage conversation and its reflection, rather than invent a denominator.
    quotas['chatbot-socratic'] = {'available': None, 'sessions_per_student': 1, 'stages_per_session': 6}
    quotas['nhat-ky-phan-tu-ai'] = {'available': None, 'entries_per_student': 1}
    start = datetime(2026, 10, 5, 2, tzinfo=timezone.utc)
    buckets = [('claim', 'Luận điểm'), ('evidence', 'Bằng chứng'), ('assumption', 'Giả định'),
               ('counter', 'Phản biện'), ('conclusion', 'Kết luận')]
    row_counts = Counter()
    for index, source_student in enumerate(students):
        username = source_student['Tài khoản']
        student = next(r for r in auth['students'] if r['username'] == username)
        teacher = next(r for r in auth['teachers'] if r['username'] == student['teacher_username'])
        rng = random.Random(identifier(username))
        common = {'student_username': username, 'student_name': student['name'],
                  'teacher_username': teacher['username'], 'teacher_name': teacher['name'],
                  'school': student['school'], 'class_name': student['class_name']}
        activities = data['activity.json'].setdefault(username, [])
        for module, filename, key, submission_key in configs:
            selected = rng.sample(pools[module], quotas[module]['distinct_per_student'])
            for exercise_index, item in enumerate(selected):
                base_score = rng.randint(42, 64)
                # Include stable/slightly lower revisions; never assert measured progress.
                gain = rng.randint(8, 24) if index % 7 else rng.choice([-3, 0, 3])
                previous = ''
                for revision in (0, 1):
                    score = max(0, min(94, base_score + gain * revision))
                    when = start + timedelta(days=revision * 12 + exercise_index, minutes=index * 3)
                    timestamp = when.isoformat()
                    entry_id = identifier(username, module, item['id'], revision)
                    provenance = stamp(source_id=item['id'], source_reference=item.get('source_reference', SOURCE),
                                       source_document=item.get('source_document', ''),
                                       attempt_number=revision + 1, previous_submission_id=previous,
                                       simulated_at=timestamp, generated_at=now)
                    review = feedback(score, item.get('source_text') or item.get('evidence') or
                                      item.get('explanation') or task_facts(item), revision)
                    entry = {**common, **provenance, 'id': entry_id, 'score': score, 'ai_score': score,
                             'teacher_score': '', 'teacher_review': '', 'status': 'pending_teacher_review',
                             'created_at': timestamp, 'submitted_at': timestamp, 'ai_review': review}
                    if module == 'nhiem-vu':
                        duration = rng.randint(650, 1450)
                        began = (when - timedelta(seconds=duration)).isoformat()
                        attempt_id = identifier(entry_id, 'attempt')
                        chat = [{**stamp(), 'role': 'student', 'content': 'Em cần đối chiếu bằng chứng nào trước khi kết luận?', 'created_at': began},
                                {**stamp(), 'role': 'assistant', 'content': LABEL + 'Hãy đối chiếu dữ kiện trong SGK và thử nêu một cách giải thích khác.', 'created_at': began}]
                        entry.update(task_id=item['id'], task_title=item['title'], prompt=item['prompt'], rubric=item['rubric'],
                                     answer=essay(item, revision, index + exercise_index), ai_review=review['feedback'],
                                     ai_meta={'model': 'simulation', **stamp()}, simulated_assessment=review,
                                     attempt_id=attempt_id, started_at=began, duration_seconds=duration, chat=chat)
                        add_unique(data[filename].setdefault('attempts', []),
                                   {**common, **provenance, 'id': attempt_id, 'task_id': item['id'],
                                    'task_title': item['title'], 'started_at': began, 'submitted_at': timestamp, 'chat': chat})
                    elif module == 'so-sanh-ba-cau-tra-loi':
                        chosen = item['best'] if revision or index % 3 else next(a['label'] for a in item['answers'] if a['label'] != item['best'])
                        reason = item.get('explanation', '')
                        answer_text = next(a['text'] for a in item['answers'] if a['label'] == chosen)
                        entry.update(package_id=item['id'], package_title=item['title'], question=item['question'], selected=chosen,
                                     correct=chosen == item['best'], criteria=f'Em chọn {chosen} vì: {answer_text}',
                                     synthesis=(reason + ' Em cần tránh kết luận tuyệt đối và kiểm tra bối cảnh.') if revision else answer_text)
                    elif module == 'tham-tu-ai':
                        entry.update(kind='detective', module_title='Thám tử thông tin', case_id=item['id'],
                                     case_code=item['code'], case_title=item['title'], task=item['task'], text=item['text'],
                                     suspicious_text=item['suspicious_text'], error_type=item['error_type'],
                                     explanation=('Em đối chiếu dữ kiện với SGK: ' + item['evidence']) if revision else 'Em nghi ngờ chi tiết này nhưng cần chỉ ra căn cứ cụ thể hơn.',
                                     evidence=item['evidence'] if revision else 'Em sẽ tìm lại bài học tương ứng trong SGK.',
                                     rewrite=item['rewrite'] if revision else 'Em chưa kết luận ngay khi chưa kiểm tra lại mốc thời gian và bối cảnh.',
                                     expected_error_type=item['error_type'], expected_suspicious_text=item['suspicious_text'],
                                     expected_evidence=item['evidence'], expected_rewrite=item['rewrite'])
                    else:
                        correct_count = min(5, max(2, round(score / 20)))
                        pieces = item['pieces']
                        placements = []
                        details = []
                        for j, piece in enumerate(pieces):
                            actual = piece['bucket'] if j < correct_count else buckets[(next(k for k, b in enumerate(buckets) if b[0] == piece['bucket']) + 1) % 5][0]
                            placements.append({'piece_id': piece['id'], 'piece_text': piece['text'], 'bucket': actual,
                                               'bucket_label': dict(buckets)[actual]})
                            details.append({'piece_id': piece['id'], 'actual': actual, 'correct': actual == piece['bucket']})
                        score = round(sum(d['correct'] for d in details) / len(pieces) * 100)
                        review = feedback(score, item['source_text'], revision)
                        entry.update(kind='argument', module_title='Bản đồ lập luận', package_id=item['id'], package_title=item['title'],
                                     question=item['question'], source_text=item['source_text'], placements=placements, details=details,
                                     total=len(pieces), correct=sum(d['correct'] for d in details), score=score, ai_score=score, ai_review=review)
                    add_unique(data[filename].setdefault(submission_key, []), entry)
                    add_unique(activities, {**provenance, 'id': identifier(entry_id, 'activity'), 'module': module,
                                           'action': 'submit' if module == 'nhiem-vu' else 'score', 'score': score,
                                           'payload': {**stamp(), 'submission_id': entry_id, 'source_id': item['id'],
                                                       'assessment': review, 'title': item['title'],
                                                       'work': {k: entry[k] for k in ('answer', 'selected', 'criteria', 'synthesis',
                                                                                     'suspicious_text', 'error_type', 'explanation',
                                                                                     'evidence', 'rewrite', 'placements') if k in entry}},
                                           'created_at': timestamp})
                    row_counts[module] += 1
                    previous = entry_id

        anchor = rng.choice(bank['argument_packages'])
        for revision in (0, 1):
            when = start + timedelta(days=5 + revision * 12, minutes=index * 3)
            prompt = ('Đóng vai người kiểm chứng lịch sử. Hãy kiểm tra nhận định: ' + anchor['pieces'][0]['text'] +
                      ' Đối chiếu với SGK Lịch sử 11, nêu căn cứ cho từng ý.')
            if revision:
                prompt += ' Chỉ ra giả định, tìm góc nhìn phản bác và nêu giới hạn; điều chỉnh kết luận theo mức độ chắc chắn của bằng chứng.'
            score = min(92, 48 + index % 13 + revision * (15 if index % 7 else 0))
            review = feedback(score, anchor['source_text'], revision)
            add_unique(activities, {**stamp(), 'id': identifier(username, 'prompt', revision), 'module': 'prompt-phan-bien',
                                   'action': 'score', 'score': score, 'created_at': when.isoformat(),
                                   'payload': {**stamp(), 'scenario_id': 'check-ai-history', 'source_id': anchor['id'],
                                               'source_reference': anchor.get('source_reference', SOURCE), 'prompt': prompt,
                                               'attempt_number': revision + 1, 'assessment': review}})
            row_counts['prompt-phan-bien'] += 1

        dialogue = []
        student_lines = [anchor['question'], 'Em đang nghiêng về ý kiến: ' + anchor['pieces'][0]['text'],
                         'Em tìm được căn cứ: ' + anchor['pieces'][1]['text'],
                         'Giả định em cần kiểm tra là: ' + anchor['pieces'][2]['text'],
                         'Em xét thêm giới hạn: ' + anchor['pieces'][3]['text'],
                         'Sau đối chiếu, em kết luận: ' + anchor['pieces'][4]['text']]
        tutor_lines = ['Em đang muốn bảo vệ luận điểm cụ thể nào?', 'Bằng chứng nào trong SGK hỗ trợ luận điểm đó?',
                       'Điều gì cần đúng để bằng chứng dẫn tới kết luận?', 'Có chi tiết nào làm hạn chế cách giải thích này?',
                       'Em sẽ sửa kết luận thế nào để phù hợp phạm vi bằng chứng?', 'Hãy ghi lại điều em đã thay đổi và phần còn cần kiểm chứng.']
        for stage in range(6):
            dialogue.extend([{'role': 'student', 'content': student_lines[stage]},
                             {'role': 'assistant', 'content': LABEL + tutor_lines[stage]}])
        session_time = (start + timedelta(days=18, minutes=index * 3)).isoformat()
        add_unique(activities, {**stamp(), 'id': identifier(username, 'socratic'), 'module': 'chatbot-socratic',
                               'action': 'session', 'score': None, 'created_at': session_time,
                               'payload': {**stamp(), 'source_id': anchor['id'], 'mode': 'easy', 'stage_index': 5,
                                           'messages': dialogue, 'board': {b[0]: anchor['pieces'][j]['text'] for j, b in enumerate(buckets)}}})
        reflection_id = identifier(username, 'reflection')
        reflection = {**stamp(), 'id': reflection_id, 'student_username': username, 'module': 'chatbot-socratic',
                      'created_at': session_time, 'answers': {'summary': anchor['question'],
                      'takeaway': LABEL + 'Ban đầu em chỉ nhìn vào một nguyên nhân. Sau khi đối chiếu: ' + anchor['pieces'][3]['text'] +
                                  ' Em cần nêu giới hạn và giữ kết luận trong phạm vi bằng chứng.'},
                      'context': {**stamp(), 'source_id': anchor['id'], 'source_reference': anchor.get('source_reference', SOURCE)}}
        add_unique(data['reflections.json'].setdefault(username, []), reflection)
        add_unique(activities, {**stamp(), 'id': identifier(reflection_id, 'activity'), 'module': 'nhat-ky-phan-tu-ai',
                               'action': 'reflection', 'score': None, 'payload': reflection, 'created_at': session_time})
        activities.sort(key=lambda r: r.get('created_at', ''))
        row_counts['chatbot-socratic'] += 1
        row_counts['nhat-ky-phan-tu-ai'] += 1

    report = {'batch': BATCH, 'synthetic_learning_data': True, 'generated_at': now, **counts,
              'teachers_in_source': len(teachers), 'students_in_source': len(students),
              'classes': [{'school': school, 'class_name': room, 'teacher_username': assignment[(school, room)]['Tài khoản'],
                           'students': sum(r['Lớp học'] == room and r['Trường'] == school for r in students)} for school, room in classes],
              'quotas': quotas, 'planned_simulated_records': dict(row_counts),
              'notes': ['20% số bài đang hoạt động, làm tròn lên; chọn nội dung Lịch sử 11 từ DATATM.',
                        'Hai lượt mỗi bài; 20% tính theo số bài khác nhau, không tính lượt sửa là bài mới.',
                        'Socratic và nhật ký không có ngân hàng bài hữu hạn: mỗi HS một phiên sáu giai đoạn và một nhật ký.',
                        'Điểm, hội thoại, nhận xét và ngày làm là mô phỏng, không phải kết quả thực nghiệm hay nhận xét của GV.',
                        'Nguồn là nội dung DATATM sẵn có; chưa OCR hoặc kiểm chứng từng trang PDF trong capnhat.',
                        'Không tạo khảo sát tự đánh giá hay đánh giá chatbot thay cho học sinh.',
                        'Không ghi điểm chốt hoặc lời nhận xét giả danh giáo viên.'],
              'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [teacher_file, student_file, source_dir / 'ghichu.txt']},
              'runtime_before_sha256': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                                       if (directory / name).exists() else None for name in FILES}}
    return data, report


def apply_plan(directory, data, report):
    manifest = directory / 'experiment-import.json'
    if manifest.exists():
        old = json.loads(manifest.read_text(encoding='utf-8'))
        if old.get('batch') == BATCH:
            raise ValueError('Đợt này đã nạp. Không ghi lại hoặc ghi đè dữ liệu đã có.')
    for name, expected in report['runtime_before_sha256'].items():
        path = directory / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != expected:
            raise ValueError('Dữ liệu đang thay đổi; hãy tạo lại bản nạp trước khi ghi.')
    backup = directory / 'backups' / (BATCH + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
    backup.mkdir(parents=True, exist_ok=False)
    original = {}
    for filename in (*FILES, 'experiment-import.json'):
        path = directory / filename
        original[filename] = path.read_bytes() if path.exists() else None
        if original[filename] is not None:
            (backup / filename).write_bytes(original[filename])
    report['backup_directory'] = str(backup)
    try:
        for filename in FILES:
            save_json(filename, data[filename])
        save_json('experiment-import.json', report)
    except BaseException:
        for filename, content in original.items():
            path = directory / filename
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--source', type=Path, default=ROOT / 'capnhat')
    args = parser.parse_args()
    with app.app_context():
        directory = Path(data_dir()).resolve()
        data, report = build_plan(directory, args.source)
        if args.apply:
            apply_plan(directory, data, report)
        print(json.dumps({'applied': args.apply, 'data_directory': str(directory), **report}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
