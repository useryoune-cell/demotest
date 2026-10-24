"""Self-report data, deliberately distinct from standardized WGCTA test scores."""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from app.services.storage import load_json, update_json
from app.services.auth_service import list_students

LOCAL_TIME = timezone(timedelta(hours=7))
MODULE_LABELS = {
    'nhiem-vu': 'Nhiệm vụ học tập', 'so-sanh-ba-cau-tra-loi': 'Đánh giá lập luận AI',
    'ban-do-lap-luan': 'Bản đồ lập luận', 'tham-tu-ai': 'Thám tử thông tin',
    'prompt-phan-bien': 'Prompt phản biện', 'chatbot-socratic': 'Chatbot Socratic',
    'nhat-ky-phan-tu-ai': 'Nhật ký phản tư', 'tin-hay-khong-tin': 'Tin hay không tin',
    'con-nguoi-truoc-ai-sau': 'Con người trước – AI sau', 'ai-co-tinh-sai': 'AI cố tình sai',
    'dau-truong-lap-luan': 'Đấu trường lập luận',
}


def _timestamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
    except (ValueError, TypeError):
        return None


def _quantity_overview(teacher_username, students, since, now):
    """Count the activity journal once; review records are a separate metric."""
    usernames = {student['username'] for student in students}
    journal = load_json('activity.json', {})
    events, seen, active = [], set(), set()
    for username in usernames:
        for row in journal.get(username, []):
            when = _timestamp(row.get('created_at'))
            if not when or not since <= when <= now or row.get('action') not in {'score', 'submit', 'session', 'reflection'}:
                continue
            identity = (username, row.get('id'))
            if row.get('id') and identity in seen:
                continue
            seen.add(identity)
            events.append((row, when))
            active.add(username)
    counts = defaultdict(lambda: {'real': 0, 'synthetic': 0})
    daily = defaultdict(lambda: {'real': 0, 'synthetic': 0})
    for row, when in events:
        kind = 'synthetic' if row.get('synthetic') or row.get('payload', {}).get('synthetic') else 'real'
        counts[row.get('module', '')][kind] += 1
        daily[when.astimezone(LOCAL_TIME).date().isoformat()][kind] += 1
    modules = [{'label': MODULE_LABELS.get(key, key), **counts[key], 'total': sum(counts[key].values())}
               for key in MODULE_LABELS]
    # Preserve unknown module activity without leaking another student's records.
    modules += [{'label': key, **value, 'total': sum(value.values())}
                for key, value in counts.items() if key not in MODULE_LABELS]
    last = now.astimezone(LOCAL_TIME).date()
    first = since.astimezone(LOCAL_TIME).date()
    if since.year == 1:
        first = min((when.astimezone(LOCAL_TIME).date() for _, when in events), default=last)
    days = []
    while first <= last:
        values = daily[first.isoformat()]
        days.append({'date': first.isoformat(), 'label': first.strftime('%d/%m'), **values, 'total': sum(values.values())})
        first += timedelta(days=1)
    review = {'pending': 0, 'reviewed': 0, 'synthetic': 0}
    for filename, keys in [('assignments.json', ['submissions']), ('compare_assignments.json', ['submissions']),
                           ('teacher_content.json', ['argument_submissions', 'detective_submissions'])]:
        data = load_json(filename, {})
        for key in keys:
            for row in data.get(key, []):
                when = _timestamp(row.get('submitted_at') or row.get('created_at'))
                if (row.get('teacher_username') != teacher_username or row.get('student_username') not in usernames
                        or not when or not since <= when <= now):
                    continue
                review['reviewed' if row.get('teacher_score') not in (None, '') else 'pending'] += 1
                review['synthetic'] += bool(row.get('synthetic'))
    synthetic = sum(row['synthetic'] for row in modules)
    return {'total_students': len(students), 'active_students': len(active), 'inactive_students': len(students) - len(active),
            'total': len(events), 'synthetic': synthetic, 'real': len(events) - synthetic,
            'modules': modules, 'days': days, 'reviews': review,
            'module_max': max([row['total'] for row in modules] + [1]),
            'day_max': max([row['total'] for row in days] + [1]),
            'review_max': max(review['pending'], review['reviewed'], 1)}

SELF_ASSESSMENT = [
    {'key': 'inference', 'label': 'Suy luận', 'question': 'Em phân biệt được điều chắc chắn với điều chỉ có thể suy ra từ thông tin đã cho.'},
    {'key': 'assumptions', 'label': 'Nhận diện giả định', 'question': 'Em tìm được điều đang được ngầm coi là đúng nhưng chưa có bằng chứng.'},
    {'key': 'deduction', 'label': 'Suy diễn', 'question': 'Em kiểm tra được kết luận có thực sự theo sau các tiền đề đã nêu hay không.'},
    {'key': 'interpretation', 'label': 'Diễn giải', 'question': 'Em đánh giá được dữ liệu có đủ để hỗ trợ cách giải thích hoặc kết luận hay không.'},
    {'key': 'arguments', 'label': 'Đánh giá lập luận', 'question': 'Em phân biệt được lý lẽ liên quan, có sức thuyết phục với lý lẽ yếu hoặc không liên quan.'},
]


def save_self_assessment(student, values):
    scores = {}
    for item in SELF_ASSESSMENT:
        raw = values.get(item['key'])
        if str(raw) not in {'1', '2', '3', '4', '5'}:
            raise ValueError('Hãy tự đánh giá đủ 5 kỹ năng từ 1 đến 5.')
        scores[item['key']] = int(raw)
    if not all(student.get(k) for k in ('school', 'class_name', 'teacher_username')):
        raise ValueError('Cần cập nhật trường, lớp và giáo viên trước.')
    entry = {k: student[k] for k in ('username', 'school', 'class_name', 'teacher_username')}
    entry.update(id=str(uuid4()), scores=scores, created_at=datetime.now(timezone.utc).isoformat(), instrument='wgcta-inspired-self-report-v1')
    update_json('learning_surveys.json', {}, lambda data: data.setdefault('self_assessments', []).append(entry))
    return entry


def save_chatbot_rating(student, module, rating, comment):
    if str(rating) not in {'1', '2', '3', '4', '5'}:
        raise ValueError('Mức đánh giá phải từ 1 đến 5.')
    entry = {k: student.get(k, '') for k in ('username', 'school', 'class_name', 'teacher_username')}
    entry.update(id=str(uuid4()), module=module, rating=int(rating), comment=str(comment or '')[:1000], created_at=datetime.now(timezone.utc).isoformat())
    update_json('learning_surveys.json', {}, lambda data: data.setdefault('chatbot_ratings', []).append(entry))
    return entry


def learning_overview(teacher_username, period='week', school='', class_name=''):
    period = period if period in {'week', 'month', 'all'} else 'week'
    students = [s for s in list_students() if s.get('teacher_username') == teacher_username]
    available = sorted({(s.get('school', ''), s.get('class_name', '')) for s in students})
    students = [s for s in students if (not school or s.get('school') == school) and (not class_name or s.get('class_name') == class_name)]
    now = datetime.now(timezone.utc)
    since = (now.astimezone(LOCAL_TIME).replace(hour=0, minute=0, second=0, microsecond=0)
             - timedelta(days=6 if period == 'week' else 29))
    if period == 'all':
        since = datetime.min.replace(tzinfo=timezone.utc)
    data = load_json('learning_surveys.json', {})
    usernames = {s['username'] for s in students}

    def visible(row):
        try:
            when = _timestamp(row['created_at'])
            return (row.get('teacher_username') == teacher_username and row.get('username') in usernames
                    and (not school or row.get('school') == school) and (not class_name or row.get('class_name') == class_name)
                    and when is not None and since <= when <= now)
        except (KeyError, ValueError, TypeError):
            return False

    # A student has one vote per class in a reporting period: use the latest self-report.
    latest = {}
    for row in sorted((r for r in data.get('self_assessments', []) if visible(r)), key=lambda r: r['created_at']):
        latest[(row['username'], row['school'], row['class_name'])] = row
    grouped = defaultdict(list)
    for row in latest.values():
        grouped[(row['school'], row['class_name'])].append(row)
    classes = []
    for (school_name, room), rows in sorted(grouped.items()):
        skills = [{'label': q['label'], 'mean': round(sum(r['scores'][q['key']] for r in rows) / len(rows), 2)} for q in SELF_ASSESSMENT]
        classes.append({'school': school_name, 'class_name': room, 'count': len(rows), 'skills': skills})
    # Keep the latest rating per student/module in the selected period.
    ratings = {}
    for row in sorted((r for r in data.get('chatbot_ratings', []) if visible(r)), key=lambda r: r['created_at']):
        ratings[(row['username'], row['module'])] = row
    buckets = [{'stars': star, 'count': sum(r['rating'] == star for r in ratings.values())} for star in range(1, 6)]
    return {'period': period, 'school': school, 'class_name': class_name, 'available_classes': available,
            'quantity': _quantity_overview(teacher_username, students, since, now),
            'classes': classes, 'ratings': buckets, 'rating_count': len(ratings),
            'rating_mean': round(sum(r['rating'] for r in ratings.values()) / len(ratings), 2) if ratings else None,
            'students': [{'name': s.get('name', s['username']), 'school': s.get('school', ''), 'class_name': s.get('class_name', '')} for s in students]}
