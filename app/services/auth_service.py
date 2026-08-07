import hmac
import os
from datetime import datetime, timezone
from uuid import uuid4

from app.services.storage import load_json, save_json

DEFAULT_TEACHER_ACCOUNTS = [
    {
        "username": "teacher01",
        "password": "teacher123",
        "name": "Giáo viên phản biện",
        "email": "teacher01@example.local",
        "active": True,
        "created_at": "demo",
    }
]

DEFAULT_STUDENT_ACCOUNTS = [
    {
        "username": "student01",
        "password": "student123",
        "name": "Học sinh demo",
        "avatar_filename": "",
        "active": True,
        "created_at": "demo",
    },
    {
        "username": "student02",
        "password": "student123",
        "name": "Học sinh demo 02",
        "avatar_filename": "",
        "active": True,
        "created_at": "demo",
    }
]

DEFAULT_AUTH_DATA = {
    "teachers": DEFAULT_TEACHER_ACCOUNTS,
    "students": DEFAULT_STUDENT_ACCOUNTS,
    "reports": [],
}


def _data():
    data = load_json("auth.json", DEFAULT_AUTH_DATA)
    changed = False
    teachers = data.setdefault("teachers", [])
    students = data.setdefault("students", [])
    data.setdefault("reports", [])

    for default_teacher in DEFAULT_TEACHER_ACCOUNTS:
        if not any(teacher.get("username") == default_teacher["username"] for teacher in teachers):
            teachers.append(default_teacher.copy())
            changed = True

    for default_student in DEFAULT_STUDENT_ACCOUNTS:
        if not any(student.get("username") == default_student["username"] for student in students):
            students.append(default_student.copy())
            changed = True

    if changed:
        save_json("auth.json", data)
    return data


def _save(data):
    save_json("auth.json", data)


def _teachers(data=None):
    return (data or _data()).setdefault("teachers", [])


def _students(data=None):
    return (data or _data()).setdefault("students", [])


def _reports(data=None):
    return (data or _data()).setdefault("reports", [])


def admin_credentials():
    return {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123"),
    }


def verify_admin(username, password):
    creds = admin_credentials()
    return hmac.compare_digest(username, creds["username"]) and hmac.compare_digest(
        password, creds["password"]
    )


def verify_teacher(username, password):
    teacher = get_teacher(username)
    if not teacher or not teacher["active"]:
        return None
    if not hmac.compare_digest(password, teacher["password"]):
        return None
    return teacher


def verify_student(username, password):
    student = get_student(username)
    if not student or not student["active"]:
        return None
    if not hmac.compare_digest(password, student["password"]):
        return None
    return student


def get_teacher(username):
    return next((teacher for teacher in _teachers() if teacher["username"] == username), None)


def get_student(username):
    return next((student for student in _students() if student["username"] == username), None)


def create_guest_student():
    data = _data()
    username = f"guest-{uuid4().hex[:10]}"
    student = {
        "username": username,
        "password": "",
        "name": "Học sinh ẩn danh",
        "avatar_filename": "",
        "active": True,
        "anonymous": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _students(data).append(student)
    _save(data)
    return student


def update_student_avatar(username, avatar_filename):
    data = _data()
    student = next((item for item in _students(data) if item["username"] == username), None)
    if not student:
        raise ValueError("Không tìm thấy tài khoản học sinh.")
    student["avatar_filename"] = str(avatar_filename or "").strip()
    _save(data)
    return student


def list_teachers():
    return _teachers()


def create_student(username, password, name):
    data = _data()
    username = str(username or "").strip()
    password = str(password or "").strip()
    if not username or not password:
        raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")
    if next((student for student in _students(data) if student["username"] == username), None):
        raise ValueError("Tên đăng nhập học sinh đã tồn tại.")

    student = {
        "username": username,
        "password": password,
        "name": str(name or username).strip(),
        "avatar_filename": "",
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _students(data).append(student)
    _save(data)
    return student


def create_teacher(username, password, name, email):
    data = _data()
    username = str(username or "").strip()
    password = str(password or "").strip()
    if not username or not password:
        raise ValueError("Username and password are required.")
    if next((teacher for teacher in _teachers(data) if teacher["username"] == username), None):
        raise ValueError("Teacher username already exists.")

    teacher = {
        "username": username,
        "password": password,
        "name": str(name or username).strip(),
        "email": str(email or "").strip(),
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _teachers(data).append(teacher)
    _save(data)
    return teacher


def toggle_teacher(username):
    data = _data()
    teacher = next((item for item in _teachers(data) if item["username"] == username), None)
    if not teacher:
        raise ValueError("Teacher not found.")
    teacher["active"] = not teacher["active"]
    _save(data)
    return teacher


def send_report(teacher_username, title, body):
    data = _data()
    teacher = next((item for item in _teachers(data) if item["username"] == teacher_username), None)
    if not teacher:
        raise ValueError("Teacher not found.")
    report = {
        "id": str(uuid4()),
        "teacher_username": teacher_username,
        "teacher_name": teacher["name"],
        "title": str(title or "Báo cáo học sinh").strip(),
        "body": str(body or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _reports(data).append(report)
    _save(data)
    return report


def reports_for_teacher(username):
    return [report for report in reversed(_reports()) if report["teacher_username"] == username]


def list_reports():
    return list(reversed(_reports()))
