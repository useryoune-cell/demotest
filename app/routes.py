from functools import wraps
import os

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from app.data.modules import AREA_SUMMARY, MODULES, get_module
from app.services.auth_service import (
    create_guest_student,
    create_student,
    create_teacher,
    get_student,
    get_teacher,
    list_reports,
    list_teachers,
    reports_for_teacher,
    send_report,
    toggle_teacher,
    update_student_avatar,
    verify_admin,
    verify_student,
    verify_teacher,
)
from app.services.dashboard_service import student_profile, teacher_overview
from app.services.debate_service import DEBATE_TOPICS, RANKS, get_rank, get_topic, judge_debate
from app.services.evaluation_bank import (
    ERROR_ITEMS,
    TRUST_ITEMS,
    get_compare_item,
    get_error_item,
    get_trust_item,
    public_error_item,
    public_trust_item,
    score_trust,
)
from app.services.game_bank import (
    ARGUMENT_MAP,
    DETECTIVE_STATIONS,
    get_detective_station,
    public_station,
    score_argument_map,
    score_detective,
)
from app.services.gemini_client import GeminiClient, GeminiClientError
from app.services.human_first_service import (
    HUMAN_FIRST_QUESTIONS,
    build_ai_after_human_prompt,
    get_human_first_question,
)
from app.services.prompt_service import PROMPT_SCENARIOS, RUBRIC, score_prompt
from app.services.reflection_store import (
    REFLECTION_QUESTIONS,
    recent_reflections,
    save_reflection,
    transfer_reflections,
)
from app.services.student_store import record_student_activity, student_activities, transfer_student_activity
from app.services.socratic_service import (
    BOARD_KEYS,
    SOCRATIC_MODES,
    SOCRATIC_STAGES,
    build_socratic_prompt,
    fallback_socratic_response,
    normalize_socratic_mode,
    parse_socratic_response,
)

main_bp = Blueprint("main", __name__)
TEACHER_MODULE_SLUG = "che-do-giao-vien"
CRITIC_ASSISTANT_SLUG = "tro-li-phan-bien"
CRITIC_ASSISTANT_CHILD_SLUGS = [
    "con-nguoi-truoc-ai-sau",
    "ai-co-tinh-sai",
    "so-sanh-ba-cau-tra-loi",
    "prompt-phan-bien",
]
CRITIC_ASSISTANT_MODULE = {
    "number": "00",
    "slug": CRITIC_ASSISTANT_SLUG,
    "title": "Trợ lí phản biện",
    "area": "Phòng luyện phản biện",
    "area_key": "training",
    "icon": "sparkles",
    "image": "images/modules/tro-li-phan-bien.png",
    "description": "Bộ trợ lí luyện kiểm chứng câu trả lời AI, so sánh, phát hiện lỗi và viết prompt phản biện.",
    "status": "4 công cụ",
    "progress": 58,
    "route_label": "Mở trợ lí",
}
ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
STUDENT_MODULES = [module for module in MODULES if module["slug"] != TEACHER_MODULE_SLUG]
CRITIC_ASSISTANT_CHILD_MODULES = [
    {**get_module(slug), "number": f"{index:02d}"}
    for index, slug in enumerate(CRITIC_ASSISTANT_CHILD_SLUGS, start=1)
    if get_module(slug)
]
_DISPLAY_MODULES = []
for module in STUDENT_MODULES:
    if module["slug"] in CRITIC_ASSISTANT_CHILD_SLUGS:
        continue
    _DISPLAY_MODULES.append(module)
    if module["slug"] == "tin-hay-khong-tin":
        _DISPLAY_MODULES.append(CRITIC_ASSISTANT_MODULE)
STUDENT_NAV_MODULES = [{**module, "number": f"{index:02d}"} for index, module in enumerate(_DISPLAY_MODULES, start=1)]
STUDENT_AREA_SUMMARY = [
    {
        **area,
        "count": sum(1 for module in STUDENT_NAV_MODULES if module["area_key"] == area["key"]),
    }
    for area in AREA_SUMMARY
    if any(module["area_key"] == area["key"] for module in STUDENT_NAV_MODULES)
]


def _auth_failure(role):
    if request.path.startswith("/api/"):
        messages = {
            "student": "Bạn cần đăng nhập học sinh để lưu dữ liệu học tập.",
            "teacher": "Bạn cần đăng nhập giáo viên để xem dữ liệu này.",
            "admin": "Bạn cần đăng nhập admin để dùng chức năng này.",
        }
        return jsonify({"error": messages.get(role, "Bạn cần đăng nhập.")}), 401
    return redirect(url_for("main.login", role=role, next=request.path))


def _set_student_session(student, is_guest=False):
    session.clear()
    session["role"] = "student"
    session["student_username"] = student["username"]
    session["student_name"] = student["name"]
    if is_guest or student.get("anonymous"):
        session["student_guest"] = True


def _start_guest_session():
    student = create_guest_student()
    _set_student_session(student, is_guest=True)
    return student


def _merge_guest_student_data(target_student, guest_username):
    if not target_student or not guest_username or target_student["username"] == guest_username:
        return
    guest_student = get_student(guest_username)
    transfer_student_activity(guest_username, target_student["username"])
    transfer_reflections(guest_username, target_student["username"])
    if guest_student and guest_student.get("avatar_filename") and not target_student.get("avatar_filename"):
        update_student_avatar(target_student["username"], guest_student["avatar_filename"])


def student_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        student = get_student(session.get("student_username")) if session.get("role") == "student" else None
        if student:
            return view(*args, **kwargs)
        if not request.path.startswith("/api/") and session.get("role") in (None, "student"):
            _start_guest_session()
            return view(*args, **kwargs)
        if session.get("role") != "student" or not student:
            return _auth_failure("student")
        return view(*args, **kwargs)

    return wrapped


def teacher_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "teacher" or not get_teacher(session.get("teacher_username")):
            return _auth_failure("teacher")
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return _auth_failure("admin")
        return view(*args, **kwargs)

    return wrapped


AVATAR_UPLOAD_TARGETS = {"ho-so-nang-luc", "nhat-ky-phan-tu-ai"}


def _avatar_target_slug():
    target = request.form.get("next") or request.args.get("next") or "ho-so-nang-luc"
    return target if target in AVATAR_UPLOAD_TARGETS else "ho-so-nang-luc"


def _avatar_redirect(message_key, message, target_slug=None):
    slug = target_slug or _avatar_target_slug()
    return redirect(url_for("main.module_detail", slug=slug, **{message_key: message}))


def _avatar_error_redirect(message, target_slug=None):
    return _avatar_redirect("avatar_error", message, target_slug)


def _allowed_avatar(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS


def _login_destination(role):
    next_path = request.args.get("next", "")
    default_paths = {
        "student": url_for("main.app_home"),
        "teacher": url_for("main.teacher_dashboard"),
        "admin": url_for("main.admin_dashboard"),
    }
    allowed_prefixes = {
        "student": ("/app", "/student"),
        "teacher": ("/teacher",),
        "admin": ("/admin",),
    }
    if next_path.startswith("/") and not next_path.startswith("//"):
        if any(next_path.startswith(prefix) for prefix in allowed_prefixes.get(role, ())):
            return next_path
    return default_paths.get(role, url_for("main.app_home"))


@main_bp.get("/")
def landing():
    return render_template("pages/landing.html")


@main_bp.get("/start")
def start_learning():
    student = get_student(session.get("student_username")) if session.get("role") == "student" else None
    if not student:
        _start_guest_session()
    return redirect(url_for("main.app_home"))


@main_bp.get("/app")
@student_required
def app_home():
    critic_assistant = next(module for module in STUDENT_NAV_MODULES if module["slug"] == CRITIC_ASSISTANT_SLUG)
    recommended = [STUDENT_NAV_MODULES[0], critic_assistant, STUDENT_NAV_MODULES[1]]
    username = session.get("student_username")
    return render_template(
        "pages/app_home.html",
        modules=STUDENT_NAV_MODULES,
        areas=STUDENT_AREA_SUMMARY,
        recommended=recommended,
        student=get_student(username),
        is_guest=session.get("student_guest", False),
    )


def _debate_view_context(**extra):
    module = get_module("dau-truong-lap-luan")
    topic_index = extra.pop("topic_index", 0)
    try:
        topic_index = int(topic_index)
    except (TypeError, ValueError):
        topic_index = 0
    rank_points = session.setdefault("debate_rank_points", 180)
    current_rank = get_rank(rank_points)
    current_rank_index = RANKS.index(current_rank)
    next_rank = RANKS[current_rank_index + 1] if current_rank_index + 1 < len(RANKS) else None
    if next_rank:
        rank_progress = max(0, min(100, rank_points - current_rank["min"]))
    else:
        rank_progress = 100
    context = {
        "module": module,
        "modules": STUDENT_NAV_MODULES,
        "topics": DEBATE_TOPICS,
        "ranks": RANKS,
        "rank": current_rank,
        "next_rank": next_rank,
        "rank_progress": rank_progress,
        "rank_points": rank_points,
        "topic_index": topic_index,
    }
    context.update(extra)
    return context


@main_bp.get("/app/modules/dau-truong-lap-luan/matching")
@student_required
def debate_matching():
    return render_template("pages/debate_matching.html", **_debate_view_context())


@main_bp.get("/app/modules/dau-truong-lap-luan/room-matching")
@student_required
def debate_room_matching():
    return render_template("pages/debate_room_matching.html", **_debate_view_context())


@main_bp.get("/app/modules/dau-truong-lap-luan/room-battle")
@student_required
def debate_room_battle():
    topic_index = request.args.get("topic", 0)
    try:
        topic_index = int(topic_index)
    except (TypeError, ValueError):
        topic_index = 0
    return render_template(
        "pages/debate_room_battle.html",
        **_debate_view_context(topic_index=topic_index, topic=get_topic(topic_index)),
    )


@main_bp.get("/app/modules/dau-truong-lap-luan/vs")
@student_required
def debate_vs():
    topic_index = request.args.get("topic", 0)
    return render_template("pages/debate_vs.html", **_debate_view_context(topic_index=topic_index))


@main_bp.get("/app/modules/dau-truong-lap-luan/battle")
@student_required
def debate_battle():
    topic_index = request.args.get("topic", 0)
    try:
        topic_index = int(topic_index)
    except (TypeError, ValueError):
        topic_index = 0
    return render_template(
        "pages/debate_battle.html",
        **_debate_view_context(topic_index=topic_index, topic=get_topic(topic_index)),
    )


@main_bp.get("/app/modules/dau-truong-lap-luan/result")
@student_required
def debate_result_page():
    result = session.get("last_debate_result")
    if not result:
        return redirect(url_for("main.module_detail", slug="dau-truong-lap-luan"))
    return render_template("pages/debate_result_page.html", **_debate_view_context(result=result))


@main_bp.get("/app/modules/<slug>")
@student_required
def module_detail(slug):
    module = get_module(slug)
    if slug == CRITIC_ASSISTANT_SLUG:
        module = CRITIC_ASSISTANT_MODULE
    if module is None:
        abort(404)
    if slug == TEACHER_MODULE_SLUG:
        abort(404)
    if slug == CRITIC_ASSISTANT_SLUG:
        return render_template(
            "pages/critic_assistant.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            child_modules=CRITIC_ASSISTANT_CHILD_MODULES,
        )
    if slug == "chatbot-socratic":
        return render_template(
            "pages/socratic_chat.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            stages=SOCRATIC_STAGES,
            board_keys=BOARD_KEYS,
        )
    if slug == "con-nguoi-truoc-ai-sau":
        return render_template(
            "pages/human_first.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            questions=HUMAN_FIRST_QUESTIONS,
        )
    if slug == "nhat-ky-phan-tu-ai":
        username = session.get("student_username")
        return render_template(
            "pages/reflection_journal.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            questions=REFLECTION_QUESTIONS,
            entries=recent_reflections(username),
            student=get_student(username),
            avatar_error=request.args.get("avatar_error", ""),
            avatar_success=request.args.get("avatar_success", ""),
        )
    if slug == "tin-hay-khong-tin":
        return render_template(
            "pages/trust_calibration.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            item=get_trust_item(0),
            item_count=len(TRUST_ITEMS),
        )
    if slug == "so-sanh-ba-cau-tra-loi":
        return render_template(
            "pages/compare_answers.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            item=get_compare_item(0),
        )
    if slug == "ai-co-tinh-sai":
        return render_template(
            "pages/intentional_error.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            levels=ERROR_ITEMS,
            item=get_error_item(1),
        )
    if slug == "tham-tu-ai":
        return render_template(
            "pages/ai_detective.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            stations=DETECTIVE_STATIONS,
            station=get_detective_station("A"),
        )
    if slug == "ban-do-lap-luan":
        return render_template(
            "pages/argument_map.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            argument_map=ARGUMENT_MAP,
        )
    if slug == "dau-truong-lap-luan":
        return render_template(
            "pages/debate_arena.html",
            **_debate_view_context(),
        )
    if slug == "prompt-phan-bien":
        return render_template(
            "pages/prompt_critic.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            scenarios=PROMPT_SCENARIOS,
            rubric=RUBRIC,
        )
    if slug == "ho-so-nang-luc":
        username = session.get("student_username")
        return render_template(
            "pages/skill_profile.html",
            module=module,
            modules=STUDENT_NAV_MODULES,
            profile=student_profile(),
            activities=student_activities(username),
            student=get_student(username),
            avatar_error=request.args.get("avatar_error", ""),
            avatar_success=request.args.get("avatar_success", ""),
        )
    return render_template("pages/module_detail.html", module=module, modules=STUDENT_NAV_MODULES)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    selected_role = request.values.get("role", "student")
    if request.method == "POST":
        selected_role = request.form.get("role", "student")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if selected_role == "student":
            student = verify_student(username, password)
            if student:
                guest_username = session.get("student_username") if session.get("student_guest") else ""
                _merge_guest_student_data(student, guest_username)
                _set_student_session(student)
                return redirect(_login_destination("student"))

        if selected_role == "admin" and verify_admin(username, password):
            session.clear()
            session["role"] = "admin"
            session["admin_username"] = username
            return redirect(_login_destination("admin"))

        if selected_role == "teacher":
            teacher = verify_teacher(username, password)
            if teacher:
                session.clear()
                session["role"] = "teacher"
                session["teacher_username"] = teacher["username"]
                session["teacher_name"] = teacher["name"]
                return redirect(_login_destination("teacher"))

        error = "Tên đăng nhập, mật khẩu hoặc vai trò không đúng."
    return render_template("pages/login.html", error=error, selected_role=selected_role)


@main_bp.route("/student/register", methods=["GET", "POST"])
def student_register():
    error = ""
    if request.method == "POST":
        guest_username = session.get("student_username") if session.get("student_guest") else ""
        try:
            student = create_student(
                username=request.form.get("username"),
                password=request.form.get("password"),
                name=request.form.get("name"),
            )
        except ValueError as exc:
            error = str(exc)
        else:
            _merge_guest_student_data(student, guest_username)
            _set_student_session(student)
            return redirect(url_for("main.app_home"))
    return render_template("pages/student_register.html", error=error)


@main_bp.route("/student/login", methods=["GET", "POST"])
def student_login():
    return redirect(url_for("main.login", role="student", next=request.args.get("next", "")))


@main_bp.get("/student/logout")
def student_logout():
    session.clear()
    return redirect(url_for("main.login", role="student"))


@main_bp.post("/student/avatar")
@student_required
def student_avatar_upload():
    target_slug = _avatar_target_slug()
    avatar = request.files.get("avatar")
    if not avatar or not avatar.filename:
        return _avatar_error_redirect("Chọn một file ảnh trước khi lưu.", target_slug)

    if not _allowed_avatar(avatar.filename):
        return _avatar_error_redirect("Avatar chỉ nhận PNG, JPG, JPEG, GIF hoặc WEBP.", target_slug)

    username = session.get("student_username")
    original_name = secure_filename(avatar.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    safe_username = secure_filename(username) or "student"
    filename = f"{safe_username}.{extension}"
    upload_dir = os.path.join(current_app.config["DATA_DIR"], "uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    avatar.save(os.path.join(upload_dir, filename))
    update_student_avatar(username, filename)
    record_student_activity(username, target_slug, "avatar")
    return _avatar_redirect("avatar_success", "Đã cập nhật avatar.", target_slug)


@main_bp.get("/uploads/avatars/<path:filename>")
def student_avatar_file(filename):
    upload_dir = os.path.join(current_app.config["DATA_DIR"], "uploads", "avatars")
    return send_from_directory(upload_dir, filename)


@main_bp.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    return redirect(url_for("main.login", role="teacher", next=request.args.get("next", "")))


@main_bp.get("/teacher/logout")
def teacher_logout():
    session.clear()
    return redirect(url_for("main.login", role="teacher"))


@main_bp.get("/teacher")
@teacher_required
def teacher_dashboard():
    username = session.get("teacher_username")
    return render_template(
        "pages/teacher_dashboard.html",
        modules=MODULES,
        overview=teacher_overview(),
        teacher=get_teacher(username),
        reports=reports_for_teacher(username),
    )


@main_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    return redirect(url_for("main.login", role="admin", next=request.args.get("next", "")))


@main_bp.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("main.login", role="admin"))


@main_bp.get("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "pages/admin_dashboard.html",
        teachers=list_teachers(),
        reports=list_reports(),
    )


@main_bp.post("/admin/teachers")
@admin_required
def admin_create_teacher():
    try:
        create_teacher(
            username=request.form.get("username"),
            password=request.form.get("password"),
            name=request.form.get("name"),
            email=request.form.get("email"),
        )
    except ValueError as exc:
        return render_template(
            "pages/admin_dashboard.html",
            teachers=list_teachers(),
            reports=list_reports(),
            error=str(exc),
        ), 400
    return redirect(url_for("main.admin_dashboard"))


@main_bp.post("/admin/teachers/<username>/toggle")
@admin_required
def admin_toggle_teacher(username):
    toggle_teacher(username)
    return redirect(url_for("main.admin_dashboard"))


@main_bp.post("/admin/reports")
@admin_required
def admin_send_report():
    try:
        send_report(
            teacher_username=request.form.get("teacher_username"),
            title=request.form.get("title"),
            body=request.form.get("body"),
        )
    except ValueError as exc:
        return render_template(
            "pages/admin_dashboard.html",
            teachers=list_teachers(),
            reports=list_reports(),
            error=str(exc),
        ), 400
    return redirect(url_for("main.admin_dashboard"))


@main_bp.get("/app/gemini")
@admin_required
def gemini_lab():
    return render_template("pages/gemini_lab.html")


@main_bp.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "service": "AI Critical Thinking Lab",
            "gemini_keys_configured": len(current_app.config["GEMINI_API_KEYS"]),
            "gemini_model": current_app.config["GEMINI_MODEL"],
        }
    )


@main_bp.get("/api/gemini/status")
@admin_required
def gemini_status():
    try:
        status = GeminiClient.status_from_app_config(current_app.config)
    except GeminiClientError as exc:
        return jsonify(
            {
                "ok": False,
                "error": str(exc),
                "model": current_app.config["GEMINI_MODEL"],
                "total_keys": len(current_app.config["GEMINI_API_KEYS"]),
                "keys": [],
            }
        )
    return jsonify({"ok": True, **status})


@main_bp.post("/api/gemini/test")
@admin_required
def gemini_test():
    prompt = (request.json or {}).get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        client = GeminiClient.from_app_config(current_app.config)
        result = client.generate_text(prompt)
    except GeminiClientError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(
        {
            "text": result.text,
            "model": result.model,
            "key_label": f"key_{result.key_index + 1}",
            "attempts": result.attempts,
        }
    )


@main_bp.post("/api/modules/socratic/message")
@student_required
def socratic_message():
    payload = request.json or {}
    messages = payload.get("messages") or []
    stage_index = payload.get("stage_index", 0)
    board = payload.get("board") or {}
    mode = normalize_socratic_mode(payload.get("mode"))

    if not messages or not str(messages[-1].get("content", "")).strip():
        return jsonify({"error": "Message is required."}), 400

    try:
        stage_index = int(stage_index)
    except (TypeError, ValueError):
        stage_index = 0

    prompt = build_socratic_prompt(messages=messages, stage_index=stage_index, board=board, mode=mode)
    try:
        client = GeminiClient.from_app_config(current_app.config)
        result = client.generate_text(prompt)
        parsed = parse_socratic_response(result.text, stage_index)
    except GeminiClientError as exc:
        return jsonify({"error": str(exc)}), 502
    except ValueError:
        parsed = fallback_socratic_response(stage_index)
        result = None

    record_student_activity(
        session.get("student_username"),
        "chatbot-socratic",
        "message",
        payload={"stage_index": stage_index, "board": board, "mode": mode},
    )
    return jsonify(
        {
            **parsed,
            "meta": {
                "model": result.model if result else current_app.config["GEMINI_MODEL"],
                "key_label": f"key_{result.key_index + 1}" if result else "fallback",
                "attempts": result.attempts if result else 0,
                "mode": mode,
                "mode_label": SOCRATIC_MODES[mode]["label"],
            },
        }
    )


@main_bp.post("/api/modules/human-first/ai-answer")
@student_required
def human_first_ai_answer():
    payload = request.json or {}
    question_id = payload.get("question_id")
    student_answer = str(payload.get("student_answer") or "").strip()
    confidence = payload.get("confidence", 50)

    if len(student_answer) < 12:
        return jsonify({"error": "Student answer is too short."}), 400

    try:
        confidence = int(confidence)
    except (TypeError, ValueError):
        confidence = 50
    confidence = min(max(confidence, 0), 100)

    question = get_human_first_question(question_id)
    prompt = build_ai_after_human_prompt(question, student_answer, confidence)

    try:
        client = GeminiClient.from_app_config(current_app.config)
        result = client.generate_text(prompt)
    except GeminiClientError as exc:
        return jsonify({"error": str(exc)}), 502

    record_student_activity(
        session.get("student_username"),
        "con-nguoi-truoc-ai-sau",
        "ai_answer",
        payload={"question_id": question_id, "confidence": confidence},
    )
    return jsonify(
        {
            "question": question,
            "ai_answer": result.text,
            "student_answer": student_answer,
            "confidence": confidence,
            "meta": {
                "model": result.model,
                "key_label": f"key_{result.key_index + 1}",
                "attempts": result.attempts,
            },
        }
    )


@main_bp.post("/api/modules/reflection")
@student_required
def reflection_save():
    payload = request.json or {}
    username = session.get("student_username")
    entry = save_reflection(payload, username)
    record_student_activity(username, payload.get("module"), "reflection", payload=entry)
    return jsonify({"ok": True, "entry": entry, "entries": recent_reflections(username)})


@main_bp.get("/api/modules/trust/item")
@student_required
def trust_item():
    index = request.args.get("index", 0)
    try:
        index = int(index)
    except (TypeError, ValueError):
        index = 0
    item = get_trust_item(index)
    return jsonify(
        {
            "item": public_trust_item(item),
            "index": index % len(TRUST_ITEMS),
            "total": len(TRUST_ITEMS),
        }
    )


@main_bp.post("/api/modules/trust/score")
@student_required
def trust_score():
    payload = request.json or {}
    item_id = payload.get("item_id")
    item = next((entry for entry in TRUST_ITEMS if entry["id"] == item_id), TRUST_ITEMS[0])
    initial = payload.get("initial", 50)
    revised = payload.get("revised", 50)
    score = score_trust(initial, revised, item["ground_truth"])
    record_student_activity(session.get("student_username"), "tin-hay-khong-tin", "score", score=score)
    return jsonify({"item": item, "score": score})


@main_bp.post("/api/modules/compare/score")
@student_required
def compare_score():
    payload = request.json or {}
    item = get_compare_item(0)
    selected = str(payload.get("selected") or "").strip().upper()
    criteria = str(payload.get("criteria") or "").strip()
    synthesis = str(payload.get("synthesis") or "").strip()
    correct = selected == item["best"]
    criteria_points = min(30, len(criteria) // 8)
    synthesis_points = min(40, len(synthesis) // 10)
    score = (30 if correct else 0) + criteria_points + synthesis_points
    final_score = min(score, 100)
    record_student_activity(session.get("student_username"), "so-sanh-ba-cau-tra-loi", "score", score=final_score)
    return jsonify(
        {
            "correct": correct,
            "best": item["best"],
            "score": final_score,
            "suggested_synthesis": item["suggested_synthesis"],
        }
    )


@main_bp.get("/api/modules/error/item")
@student_required
def error_item():
    level = request.args.get("level", 1)
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 1
    return jsonify({"item": public_error_item(get_error_item(level))})


@main_bp.post("/api/modules/error/score")
@student_required
def error_score():
    payload = request.json or {}
    item = get_error_item(payload.get("level", 1))
    chosen_type = str(payload.get("error_type") or "").strip()
    explanation = str(payload.get("explanation") or "").strip()
    rewrite = str(payload.get("rewrite") or "").strip()
    evidence = str(payload.get("evidence") or "").strip()
    suspicious = str(payload.get("suspicious_text") or "").strip().lower()

    points = 0
    if chosen_type == item["error_type"]:
        points += 25
    if item["suspicious_text"].lower() in suspicious or suspicious in item["suspicious_text"].lower():
        points += 20
    points += min(20, len(explanation) // 8)
    points += min(20, len(rewrite) // 10)
    points += min(15, len(evidence) // 8)

    final_score = min(points, 100)
    record_student_activity(session.get("student_username"), "ai-co-tinh-sai", "score", score=final_score)
    return jsonify(
        {
            "score": final_score,
            "expected": item,
            "matched_type": chosen_type == item["error_type"],
        }
    )


@main_bp.get("/api/modules/detective/station")
@student_required
def detective_station():
    code = request.args.get("code", "A")
    station = get_detective_station(code)
    return jsonify({"station": public_station(station)})


@main_bp.post("/api/modules/detective/score")
@student_required
def detective_score():
    payload = request.json or {}
    result = score_detective(
        code=payload.get("code", "A"),
        suspicious_text=payload.get("suspicious_text", ""),
        error_type=payload.get("error_type", ""),
        explanation=payload.get("explanation", ""),
        evidence=payload.get("evidence", ""),
        rewrite=payload.get("rewrite", ""),
    )
    record_student_activity(session.get("student_username"), "tham-tu-ai", "score", score=result.get("score"))
    return jsonify(result)


@main_bp.get("/api/modules/argument-map")
@student_required
def argument_map_item():
    return jsonify({"argument_map": ARGUMENT_MAP})


@main_bp.post("/api/modules/argument-map/score")
@student_required
def argument_map_score():
    payload = request.json or {}
    result = score_argument_map(payload.get("placements") or {})
    record_student_activity(session.get("student_username"), "ban-do-lap-luan", "score", score=result.get("score"))
    return jsonify(result)


@main_bp.get("/api/modules/debate/topic")
@student_required
def debate_topic():
    topic = get_topic(request.args.get("index", 0))
    return jsonify({"topic": topic, "total": len(DEBATE_TOPICS)})


@main_bp.post("/api/modules/debate/judge")
@student_required
def debate_judge():
    payload = request.json or {}
    topic = get_topic(payload.get("topic_index", 0))
    player_argument = str(payload.get("player_argument") or "").strip()
    opponent_argument = str(payload.get("opponent_argument") or "").strip()
    mode = str(payload.get("mode") or "solo").strip()

    if len(player_argument) < 20:
        return jsonify({"error": "Lập luận cần dài hơn một chút trước khi chấm."}), 400

    result = judge_debate(
        topic=topic,
        player_argument=player_argument,
        opponent_argument=opponent_argument,
        mode=mode,
    )
    current_points = int(session.get("debate_rank_points", 180) or 180)
    previous_rank = get_rank(current_points)
    if result["winner"] == "opponent" and current_points < 200:
        result["rank_delta"] = 0
    new_points = max(0, current_points + result["rank_delta"])
    session["debate_rank_points"] = new_points
    result["previous_rank"] = previous_rank
    result["previous_rank_points"] = current_points
    result["rank"] = get_rank(new_points)
    result["rank_points"] = new_points
    result["result_url"] = url_for("main.debate_result_page")
    session["last_debate_result"] = result
    record_student_activity(session.get("student_username"), "dau-truong-lap-luan", "score", score=result["player"]["total"])
    return jsonify(result)


@main_bp.post("/api/modules/prompt/score")
@student_required
def prompt_score():
    payload = request.json or {}
    prompt = str(payload.get("prompt") or "").strip()
    if len(prompt) < 12:
        return jsonify({"error": "Prompt is too short."}), 400
    result = score_prompt(prompt)
    record_student_activity(session.get("student_username"), "prompt-phan-bien", "score", score=result.get("score"))
    return jsonify(result)


@main_bp.get("/api/modules/profile")
@student_required
def profile_data():
    return jsonify(
        {
            "profile": student_profile(),
            "activities": student_activities(session.get("student_username")),
        }
    )


@main_bp.get("/api/teacher/overview")
@teacher_required
def teacher_overview_api():
    return jsonify({"overview": teacher_overview()})
