## app/templates/base.html

```html
<!doctype html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}AI Critical Thinking Lab{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    {% if request.endpoint in ['main.landing', 'main.app_home'] %}
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
    {% else %}
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    {% endif %}
    <script>
        (function () {
            try {
                if (localStorage.getItem("ct-theme") === "dark") {
                    document.documentElement.classList.add("theme-dark");
                }
            } catch (error) {
                document.documentElement.classList.remove("theme-dark");
            }
        })();
    </script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css', v='legacy-58eb4a1') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/learning-feedback.css', v='assignment-fix-2') }}">
    {% block head %}{% endblock %}
    {% if request.endpoint not in ['main.landing', 'main.app_home'] %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/design-tokens.css', v='notebook-1') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/design-system.css', v='notebook-1') }}">
    {% endif %}
</head>
<body class="{% block body_class %}{% endblock %}{% if session.get('role') %} is-authenticated{% endif %}{% if request.path.startswith('/app/modules/') %} module-focus-page{% endif %}">
    {% if request.path.startswith('/app/modules/') %}
    <a class="module-focus-back" href="{{ url_for('main.app_home') }}">
        <i data-lucide="arrow-left"></i>
        <span>Quay lại</span>
    </a>
    {% endif %}
    <header class="site-header">
        <a class="brand" href="{{ url_for('main.landing') }}" aria-label="AI Critical Thinking Lab">
            <span class="brand-mark">AI</span>
            <span>Critical Thinking Lab</span>
        </a>
        <nav class="main-nav" aria-label="Điều hướng chính">
            <a href="{{ url_for('main.landing') }}">Trang chủ</a>
            {% if request.endpoint == "main.landing" %}
            <a href="{{ url_for('main.landing') }}#features">Tính năng</a>
            {% endif %}
            {% if not session.get('role') %}<a href="{{ url_for('main.login', role='student') }}">Đăng nhập</a>{% endif %}
        </nav>
        <div class="header-actions">
            {% if request.endpoint != "main.landing" %}
            <button class="theme-toggle" type="button" data-theme-toggle aria-label="Chuyển chế độ tối">
                <i data-lucide="moon"></i>
            </button>
            {% endif %}
            {% if session.get('role') %}
            <details class="account-menu">
                <summary>{{ session.get('student_name') or session.get('teacher_name') or session.get('admin_username') }}</summary>
                {% if session.role == 'student' %}<a href="{{ url_for('main.learning_profile') }}">Trường, lớp và tự đánh giá</a>{% endif %}
                {% if session.role == 'teacher' %}<a href="{{ url_for('main.teacher_dashboard') }}">Trang giáo viên</a>{% endif %}
                {% if session.role == 'admin' %}<a href="{{ url_for('main.admin_dashboard') }}">Trang quản trị</a>{% endif %}
                <a href="{{ url_for('main.' + session.role + '_logout') }}">Đăng xuất</a>
            </details>
            {% else %}<a class="header-cta" href="{{ url_for('main.start_learning') }}">Bắt đầu</a>{% endif %}
        </div>
    </header>

    <main>
        {% for message in get_flashed_messages() %}<p class="app-panel" role="alert">{{ message }}</p>{% endfor %}
        {% block content %}{% endblock %}
    </main>

    <footer class="site-footer">
        <span>© 2026 · AI Critical Thinking Lab</span>
    </footer>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
    <script src="{{ url_for('static', filename='js/learning-feedback.js', v='learning-1') }}"></script>
    <script src="{{ url_for('static', filename='js/main.js', v='workshop-1') }}"></script>
    {% block scripts %}{% endblock %}
    {% if request.endpoint not in ['main.landing', 'main.app_home'] %}
    <script src="{{ url_for('static', filename='js/design-system.js', v='notebook-1') }}"></script>
    {% endif %}
</body>
</html>

```

## app/templates/pages/admin_dashboard.html

```html
{% extends "base.html" %}

{% block title %}Quản trị hệ thống · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell admin-shell">
    <aside class="app-sidebar" aria-label="Điều hướng quản trị">
        <a class="sidebar-item active" href="{{ url_for('main.admin_dashboard') }}"><i data-lucide="shield"></i><span>Quản trị</span></a>
        <a class="sidebar-item" href="#teacherAccounts"><i data-lucide="users"></i><span>Giáo viên</span></a>
        <a class="sidebar-item" href="#adminReports"><i data-lucide="send"></i><span>Báo cáo</span></a>
        <a class="sidebar-item" href="{{ url_for('main.gemini_lab') }}"><i data-lucide="sparkles"></i><span>Cấu hình hệ thống</span></a>
        <a class="sidebar-item" href="{{ url_for('main.admin_logout') }}"><i data-lucide="log-out"></i><span>Thoát</span></a>
    </aside>

    <section class="app-content">
        <div class="teacher-top">
            <div>
                <p class="eyebrow dark">Quản trị</p>
                <h1>Quản lý tài khoản giáo viên</h1>
            </div>
        </div>

        {% if error %}<div class="auth-error wide">{{ error }}</div>{% endif %}

        <div class="admin-grid">
            <section class="app-panel" id="teacherAccounts">
                <div class="panel-heading"><div><p class="eyebrow dark">Tài khoản</p><h2>Danh sách giáo viên</h2></div></div>
                <div class="teacher-account-list">
                    {% for teacher in teachers %}
                    <article>
                        <div>
                            <strong>{{ teacher.name }}</strong>
                            <span>{{ teacher.username }} · {{ teacher.email or "chưa có email" }}</span>
                        </div>
                        <em class="{% if teacher.active %}active{% endif %}">{{ "Đang hoạt động" if teacher.active else "Đã khóa" }}</em>
                        <form method="post" action="{{ url_for('main.admin_toggle_teacher', username=teacher.username) }}">
                            <button type="submit">{{ "Khóa" if teacher.active else "Mở" }}</button>
                        </form>
                    </article>
                    {% endfor %}
                </div>
            </section>

            <form class="app-panel admin-form" method="post" action="{{ url_for('main.admin_create_teacher') }}">
                <div class="panel-heading"><div><p class="eyebrow dark">Cấp phát</p><h2>Tạo giáo viên</h2></div></div>
                <label class="field-label" for="teacherName">Tên hiển thị</label>
                <input id="teacherName" name="name" placeholder="Giáo viên phản biện">
                <label class="field-label" for="teacherEmail">Email</label>
                <input id="teacherEmail" name="email" type="email" placeholder="teacher@example.com">
                <label class="field-label" for="teacherUsername">Tên đăng nhập</label>
                <input id="teacherUsername" name="username" required>
                <label class="field-label" for="teacherPassword">Mật khẩu</label>
                <div class="password-field">
                    <input id="teacherPassword" name="password" type="password" required>
                    <button type="button" class="password-toggle" data-password-toggle="teacherPassword" aria-label="Hiện mật khẩu"><i data-lucide="eye"></i></button>
                </div>
                <button class="button primary" type="submit"><i data-lucide="user-plus"></i><span>Tạo tài khoản</span></button>
            </form>
        </div>

        <div class="admin-grid lower" id="adminReports">
            <form class="app-panel admin-form" method="post" action="{{ url_for('main.admin_send_report') }}">
                <div class="panel-heading"><div><p class="eyebrow dark">Báo cáo</p><h2>Gửi cho giáo viên</h2></div></div>
                <label class="field-label" for="reportTeacher">Giáo viên nhận</label>
                <select id="reportTeacher" name="teacher_username" required>
                    {% for teacher in teachers %}
                    <option value="{{ teacher.username }}">{{ teacher.name }} · {{ teacher.username }}</option>
                    {% endfor %}
                </select>
                <label class="field-label" for="reportTitle">Tiêu đề</label>
                <input id="reportTitle" name="title" value="Báo cáo tiến độ học sinh">
                <label class="field-label" for="reportBody">Nội dung</label>
                <textarea id="reportBody" name="body" rows="6">Học sinh cần tăng hoạt động kiểm chứng đa nguồn và giảm phụ thuộc gợi ý AI.</textarea>
                <button class="button primary" type="submit"><i data-lucide="send"></i><span>Gửi báo cáo</span></button>
            </form>

            <section class="app-panel">
                <div class="panel-heading"><div><p class="eyebrow dark">Đã gửi</p><h2>Lịch sử báo cáo</h2></div></div>
                <div class="report-list">
                    {% if reports %}
                        {% for report in reports %}
                        <article>
                            <span>{{ report.teacher_name }}</span>
                            <strong>{{ report.title }}</strong>
                            <p>{{ report.body }}</p>
                        </article>
                        {% endfor %}
                    {% else %}
                        <p class="muted-note">Chưa có báo cáo.</p>
                    {% endif %}
                </div>
            </section>
        </div>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/admin_login.html

```html
{% extends "base.html" %}

{% block title %}Admin · AI Critical Thinking Lab{% endblock %}

{% block content %}
<section class="auth-page admin-auth">
    <form class="auth-card" method="post">
        <p class="eyebrow dark">Quản trị</p>
        <h1>Quản trị hệ thống</h1>
        {% if error %}<div class="auth-error">{{ error }}</div>{% endif %}
        <label class="field-label" for="username">Tên đăng nhập</label>
        <input id="username" name="username" autocomplete="username" required>
        <label class="field-label" for="password">Mật khẩu</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required>
        <button class="button primary" type="submit"><i data-lucide="shield-check"></i><span>Đăng nhập quản trị</span></button>
    </form>
</section>
{% endblock %}

```

## app/templates/pages/ai_detective.html

```html
{% extends "base.html" %}

{% block title %}Thám tử AI · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content detective-page">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1><i class="ti ti-file-off"></i><span>{{ module.title }}</span></h1>
            </div>
            <a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">
                <i class="ti ti-folder"></i><span>Đổi lĩnh vực</span>
            </a>
        </div>

        <section class="detective-map" aria-label="Manh mối Thám tử AI">
            {% for station_item in stations %}
            <button class="detective-node {% if loop.first %}active current{% endif %}" type="button" data-station-code="{{ station_item.code }}" {% if not loop.first %}disabled{% endif %}>
                <span>{{ station_item.code }}</span>
                <small>{{ station_item.title }}</small>
                <i class="ti {% if loop.first %}ti-file-off{% else %}ti-lock{% endif %}"></i>
            </button>
            {% endfor %}
        </section>

        <section class="detective-layout">
            <article class="app-panel detective-task" id="detectiveTask" data-code="{{ station.code }}" data-field="{{ field_key }}">
                <p class="eyebrow dark" id="detectiveTaskLabel">{{ station.code }} · {{ station.title }}</p>
                <h2 id="detectiveTaskTitle">{{ station.task }}</h2>
                <div class="ai-answer-box selectable" id="detectiveText">{{ station.text }}</div>
                <div class="detective-hint">
                    <i class="ti ti-bulb"></i>
                    <div>
                        <strong>Gợi ý</strong>
                        <p>Khoanh vùng câu có số liệu, nguồn dẫn hoặc kết luận quá chắc chắn. Sau đó đối chiếu với nguồn độc lập trước khi viết lại.</p>
                    </div>
                </div>
            </article>

            <form class="app-panel detective-form" id="detectiveForm">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Phân tích</p>
                        <h2>Kiểm chứng</h2>
                    </div>
                    <span class="response-meta" id="detectiveMeta"></span>
                </div>
                <label class="field-label" for="detectiveSuspicious">Đoạn đáng nghi</label>
                <textarea id="detectiveSuspicious" rows="2" required></textarea>
                <label class="field-label" for="detectiveType">Loại lỗi</label>
                <select id="detectiveType">
                    <option>Dữ kiện sai</option>
                    <option>Nguồn không tồn tại</option>
                    <option>Suy luận thiếu căn cứ</option>
                    <option>Khái quát hóa quá mức</option>
                    <option>Đúng nhưng sai bối cảnh</option>
                    <option>Thiên lệch</option>
                </select>
                <label class="field-label" for="detectiveExplanation">Vì sao đáng nghi?</label>
                <textarea id="detectiveExplanation" rows="3" required></textarea>
                <label class="field-label" for="detectiveEvidence">Nguồn/bằng chứng kiểm chứng</label>
                <textarea id="detectiveEvidence" rows="3" required></textarea>
                <label class="field-label" for="detectiveRewrite">Viết lại chính xác hơn</label>
                <textarea id="detectiveRewrite" rows="4" required></textarea>
                <button class="button primary" type="submit"><i class="ti ti-gavel"></i><span>Phá án</span></button>
            </form>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/argument_map.html

```html
{% extends "base.html" %}

{% block title %}Bản đồ lập luận · AI Critical Thinking Lab{% endblock %}

{% block content %}
{% set bucket_icons = {
    "claim": "ti-flag",
    "evidence": "ti-file-check",
    "assumption": "ti-question-mark",
    "counter": "ti-message-question",
    "conclusion": "ti-flag-2"
} %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content argument-page">
        <div class="module-detail-hero">
            <div>
                <h1><i class="ti ti-map-2"></i><span>{{ module.title }}</span></h1>
            </div>
            <button class="button primary" type="button" id="scoreArgumentMap"><i class="ti ti-check"></i><span>Chấm bản đồ</span></button>
        </div>

        <section class="argument-source">
            <p class="eyebrow dark">Câu hỏi</p>
            <h2>{{ argument_map.question }}</h2>
            {% if argument_map.source_text %}
            <p class="argument-source-text">{{ argument_map.source_text }}</p>
            {% endif %}
        </section>

        <section class="argument-workspace" data-map-id="{{ argument_map.id }}">
            <aside class="piece-tray">
                <div class="panel-heading">
                    <div>
                        <h2><i class="ti ti-list"></i><span>Phân loại</span></h2>
                    </div>
                </div>
                <div class="argument-pieces" id="argumentPieces">
                    {% for piece in argument_map.pieces %}
                    <article class="argument-piece" draggable="true" data-piece-id="{{ piece.id }}">
                        {{ piece.text }}
                    </article>
                    {% endfor %}
                </div>
            </aside>

            <section class="argument-canvas" aria-label="Vùng phân loại bản đồ lập luận">
                {% for bucket in argument_map.buckets %}
                <div class="argument-bucket" data-bucket-key="{{ bucket.key }}">
                    <h3><i class="ti {{ bucket_icons.get(bucket.key, 'ti-circle') }}"></i><span>{{ bucket.label }}</span></h3>
                    <div class="bucket-dropzone"></div>
                </div>
                {% endfor %}
            </section>
        </section>

        <section class="app-panel argument-result argument-complete" id="argumentResult" hidden>
            <div class="panel-heading">
                <div>
                    <p class="eyebrow dark">Kết quả</p>
                    <h2 id="argumentScore">0/100</h2>
                </div>
                <span class="argument-result-badge" id="argumentResultBadge">Đang chấm</span>
            </div>
            <h3 id="argumentResultTitle">Bản đồ đã được chấm</h3>
            <p id="argumentFeedback"></p>
            <p id="argumentReflection"></p>
            <div class="argument-result-actions">
                <button class="button secondary" type="button" id="retryArgumentMap">
                    <i data-lucide="rotate-ccw"></i><span>Làm lại</span>
                </button>
                <a class="button secondary" href="{{ url_for('main.app_home') }}">
                    <i data-lucide="layout-grid"></i><span>Về bảng học</span>
                </a>
                <a class="button primary" href="{{ url_for('main.module_detail', slug='prompt-phan-bien') }}" id="nextArgumentModule">
                    <i data-lucide="arrow-right"></i><span>Bài tiếp theo</span>
                </a>
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/argument_packages.html

```html
{% extends "base.html" %}

{% block title %}Bản đồ lập luận · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content assignment-list-page">
        <div class="module-detail-hero">
            <div><h1>{{ module.title }}</h1></div>
        </div>

        <section class="assignment-task-grid" aria-label="Danh sách gói bản đồ lập luận">
            {% if packages %}
                {% for package in packages %}
                <a class="assignment-task-box" href="{{ url_for('main.argument_map_work', map_id=package.id) }}">
                    <span class="assignment-task-icon"><i data-lucide="workflow"></i></span>
                    <strong>{{ package.title }}</strong>
                    <em>{{ package.teacher_name }}</em>
                    <p>{{ package.question|truncate(140) }}</p>
                    <span class="assignment-task-action">Vào phân loại <i data-lucide="arrow-right"></i></span>
                </a>
                {% endfor %}
            {% else %}
                <article class="app-panel assignment-empty">
                    <i data-lucide="workflow"></i>
                    <h2>Chưa có gói bản đồ đang mở</h2>
                </article>
            {% endif %}
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/assignment_work.html

```html
{% extends "base.html" %}
{% block title %}{{ task.title }} · Nhiệm vụ học tập{% endblock %}
{% block body_class %}workshop-page {% endblock %}
{% block head %}<link rel="stylesheet" href="{{ url_for('static', filename='css/workshop.css', v='workshop-1') }}">{% endblock %}
{% block content %}
<div class="app-shell module-shell">
    {% include 'pages/workshop_sidebar.html' %}
    <section class="app-content workshop-content assignment-page" data-task-id="{{ task.id }}" data-student-key="{{ session.get('student_username', '') }}" data-consent="{{ 'yes' if consent_accepted else 'no' }}">
        <nav class="workshop-breadcrumb" aria-label="Đường dẫn"><a href="{{ url_for('main.app_home') }}"><i data-lucide="house"></i></a><span>/</span><a href="{{ url_for('main.module_detail', slug=module.slug) }}">Nhiệm vụ học tập</a><span>/</span><span>Không gian làm bài</span></nav>
        <header class="module-detail-hero assignment-work-hero">
            <div><span class="task-subject">{{ 'Lịch sử 11' if task.get('source_document') or 'SGK' in task.rubric else 'Tư duy phản biện' }}</span><h1>{{ task.title }}</h1><div class="assignment-work-meta"><span><i data-lucide="pencil-line"></i> Viết lập luận</span><span><i data-lucide="book-open"></i> Đối chiếu tài liệu đã học</span></div></div>
            <div class="assignment-timer" aria-label="Thời gian làm bài"><i class="ti ti-clock"></i><div><span>Đã làm được</span><strong id="assignmentTimer">00:00</strong></div><small id="assignmentTimerState">Đang chờ</small></div>
        </header>
        <section class="assignment-workspace">
            <article class="workshop-card assignment-task-card">
                <div class="workshop-heading"><span class="section-icon blue"><i data-lucide="file-text"></i></span><div><h2>Đề bài</h2><p>Đọc kỹ nhận định và yêu cầu trước khi viết.</p></div></div>
                <p class="assignment-full-prompt">{{ task.prompt }}</p>
            </article>
            <aside class="workshop-card assignment-direction">
                <details open><summary><span><i data-lucide="lightbulb"></i> Gợi ý định hướng</span><i data-lucide="chevron-down"></i></summary>
                    <ol class="direction-steps"><li><span>1</span><div><strong>Xác định quan điểm</strong><p>Em đồng ý, không đồng ý hay chỉ đồng ý một phần?</p></div></li><li><span>2</span><div><strong>Lựa chọn bằng chứng</strong><p>Tìm dữ kiện cụ thể trong tài liệu để bảo vệ quan điểm.</p></div></li><li><span>3</span><div><strong>Phân tích, đối chiếu</strong><p>Bằng chứng dẫn đến kết luận thế nào? Có góc nhìn khác không?</p></div></li><li><span>4</span><div><strong>Kết luận có căn cứ</strong><p>Nêu nhận định của em và giới hạn còn cần kiểm chứng.</p></div></li></ol>
                </details>
            </aside>
            <form class="workshop-card assignment-form" id="assignmentForm">
                <div class="workshop-heading"><span class="section-icon blue"><i data-lucide="notebook-pen"></i></span><div><h2>Bài làm của em</h2><p>Diễn đạt bằng suy nghĩ và lời văn của chính em.</p></div><span class="assignment-counter" id="assignmentCounter">0 từ · 0 ký tự</span></div>
                <div class="assignment-writing-grid">
                    <div class="assignment-answer-wrap"><label class="visually-hidden" for="assignmentAnswer">Bài làm của em</label><textarea id="assignmentAnswer" rows="11" placeholder="Bắt đầu với quan điểm của em, sau đó dùng bằng chứng để giải thích…" required></textarea><p class="editor-note"><i data-lucide="shield-check"></i> Kiểm chứng thông tin AI trước khi đưa vào bài.</p></div>
                    <aside class="assignment-rubric-card"><h3><i data-lucide="clipboard-check"></i> Tiêu chí chấm</h3><div class="assignment-rubric-criteria">{% for line in task.rubric.split('\n') %}{% if line.strip() and not line.startswith(('Rubric', 'SGK', 'Nội dung nhiệm vụ')) %}<p><span class="rubric-dot"></span>{{ line }}</p>{% endif %}{% endfor %}</div><details><summary>Xem rubric đầy đủ</summary><p class="rubric-original">{{ task.rubric }}</p></details></aside>
                </div>
                <div class="assignment-submit-bar"><div><button class="button secondary" id="assignmentSaveDraft" type="button"><i data-lucide="save"></i><span>Lưu nháp</span></button><span id="assignmentDraftStatus" class="draft-status" role="status"></span></div><button class="button primary" type="submit"><i class="ti ti-send"></i><span>Nộp bài</span></button></div>
                <p class="response-meta workshop-status" id="assignmentMeta" role="status" aria-live="polite"></p>
            </form>
        </section>
        <aside class="assignment-chatbot" id="assignmentChatbot" aria-label="AI hỗ trợ em suy nghĩ">
            <button class="assignment-chat-toggle" type="button" id="assignmentChatToggle" aria-label="Mở chatbot" aria-expanded="false"><i data-lucide="bot"></i><span><strong>AI hỗ trợ em suy nghĩ</strong><small>Bí ý? Hỏi để được gợi mở, kiểm tra căn cứ hoặc xem một góc nhìn khác.</small></span><span class="chat-open-label">Đặt câu hỏi <i data-lucide="arrow-right"></i></span></button>
            <div class="assignment-chat-panel" id="assignmentChatPanel" hidden><div class="assignment-chat-head"><div><strong>AI hỗ trợ em suy nghĩ</strong><small>Gợi mở để em tự viết bài.</small></div><button type="button" id="assignmentChatClose" aria-label="Đóng"><i data-lucide="x"></i></button></div><div class="assignment-chat-thread" id="assignmentChatThread"><article class="socratic-message ai"><span>AI</span><p>Em đang cần làm rõ quan điểm, tìm căn cứ hay kiểm tra một cách lập luận?</p></article></div><form class="assignment-chat-form" id="assignmentChatForm"><label class="visually-hidden" for="assignmentChatInput">Câu hỏi cho AI</label><textarea id="assignmentChatInput" rows="2" placeholder="Nhập câu hỏi để AI gợi mở…"></textarea><button type="submit" aria-label="Gửi"><i class="ti ti-send"></i><span>Gửi câu hỏi</span></button></form></div>
        </aside>
        <section class="workshop-card assignment-result" id="assignmentResult" hidden><div class="workshop-heading"><span class="section-icon green"><i data-lucide="message-square-text"></i></span><div><h2>Nhận xét để em tiến bộ</h2><p>AI nhận xét sơ bộ; giáo viên sẽ chốt đánh giá.</p></div></div><p id="assignmentAiReview"></p></section>
        <div class="assignment-consent" id="assignmentConsent" role="dialog" aria-modal="true" aria-labelledby="assignmentConsentTitle" hidden><div class="assignment-consent-card"><i data-lucide="shield-check"></i><span class="assignment-consent-badge">Trước khi làm bài</span><h2 id="assignmentConsentTitle">Lưu lại hành trình suy nghĩ của em</h2><p>Thời gian làm bài, nội dung nộp và trao đổi với AI được lưu để giáo viên theo dõi và hỗ trợ em.</p><div><button class="button primary assignment-accept" type="button" id="acceptAssignmentConsent"><i class="ti ti-shield-check"></i><span>Tôi đồng ý</span></button><a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">Quay lại</a></div></div></div>
    </section>
</div>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', filename='js/workshop.js', v='workshop-1') }}"></script>{% endblock %}

```

## app/templates/pages/compare_answers.html

```html
{% extends "base.html" %}

{% block title %}So sánh ba câu trả lời AI · AI Critical Thinking Lab{% endblock %}

{% block content %}
{% set trust_badges = {
    "source": {"label": "Có nguồn", "icon": "ti-shield-check"},
    "unclear": {"label": "Mơ hồ", "icon": "ti-alert-triangle"},
    "no_source": {"label": "Không nguồn", "icon": "ti-shield-x"}
} %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content compare-page">
        <div class="module-detail-hero">
            <div>
                <h1>{{ module.title }}</h1>
                {% if item %}
                <p>{{ item.question }}</p>
                {% endif %}
            </div>
            {% if item %}
            <a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">
                <i class="ti ti-folder"></i><span>Đổi đề</span>
            </a>
            {% endif %}
        </div>

        {% if not item %}
        <section class="app-panel compare-package-panel">
            <div class="panel-heading">
                <div><h2>Kho đề</h2></div>
            </div>
            {% if packages %}
            <div class="compare-package-list">
                {% for package in packages %}
                <a class="compare-package-card" href="{{ url_for('main.module_detail', slug=module.slug, package=package.id) }}">
                    <strong>{{ package.title }}</strong>
                    <span>{{ package.teacher_name }}</span>
                    <em>Vào làm bài</em>
                </a>
                {% endfor %}
            </div>
            {% else %}
            <p class="muted-note">Chưa có gói bài từ giáo viên.</p>
            {% endif %}
        </section>
        {% endif %}

        {% if item %}
        <section class="compare-grid">
            {% for answer in item.answers %}
            {% set badge = trust_badges.get(answer.trust, trust_badges["unclear"]) %}
            <article class="compare-card compare-card-{{ answer.label|lower }}" data-answer-label="{{ answer.label }}">
                <span class="trust-badge trust-{{ answer.trust or 'unclear' }}"><i class="ti {{ badge.icon }}"></i>{{ badge.label }}</span>
                <span class="module-number">{{ answer.label }}</span>
                <p>{{ answer.text }}</p>
            </article>
            {% endfor %}
        </section>

        <form class="compare-form" id="compareForm" data-package-id="{{ item.id }}">
            <div class="panel-heading">
                <div><h2><i class="ti ti-pencil"></i><span>Tự nhận định và lập luận</span></h2></div>
                <span class="response-meta" id="compareMeta" aria-live="polite"></span>
            </div>
            <div class="choice-row">
                <input type="hidden" name="bestAnswer" value="">
                {% for answer in item.answers %}
                <button class="compare-choice-button" type="button" data-answer-value="{{ answer.label }}">
                    <i class="ti ti-check"></i>
                    <span>Câu {{ answer.label }}</span>
                </button>
                {% endfor %}
            </div>
            <label class="field-label" for="compareCriteria">Vì sao em chọn câu đó?</label>
            <textarea id="compareCriteria" rows="4" minlength="20" required placeholder="Nhập lý do chọn..."></textarea>
            <label class="field-label" for="compareSynthesis">Câu trả lời em tự viết lại</label>
            <textarea id="compareSynthesis" rows="5" minlength="30" required></textarea>
            <button class="button primary" type="submit"><i class="ti ti-send"></i><span>Lưu đánh giá</span></button>
        </form>
        {% endif %}
    </section>
</div>
{% endblock %}

```

## app/templates/pages/critic_assistant.html

```html
{% extends "base.html" %}

{% block title %}Trợ lí phản biện · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for item in modules %}
        <a class="sidebar-item {% if item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=item.slug) }}">
            <i data-lucide="{{ item.icon }}"></i><span>{{ item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
        </div>

        <section class="app-panel">
            <div class="module-grid app-module-grid critic-assistant-grid avatar-only-grid">
                {% for child in child_modules %}
                <a class="module-avatar-card app-module-card" href="{{ url_for('main.module_detail', slug=child.slug) }}" aria-label="{{ child.title }}">
                    {% if child.image %}
                    <img class="module-avatar" src="{{ url_for('static', filename=child.image, v='module-avatar-vertical-2') }}" alt="">
                    <span class="module-avatar-fallback" hidden><i data-lucide="{{ child.icon }}"></i></span>
                    {% else %}
                    <span class="module-avatar-fallback"><i data-lucide="{{ child.icon }}"></i></span>
                    {% endif %}
                    <strong>{{ child.title }}</strong>
                </a>
                {% endfor %}
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_arena.html

```html
{% extends "base.html" %}

{% block title %}Đấu trường lập luận · AI Critical Thinking Lab{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero debate-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <div class="rank-badge" style="--rank-color: {{ rank.color }}">
                <div class="rank-emblem">
                    <i data-lucide="shield"></i>
                </div>
                <span>{{ rank.name }}</span>
                <strong id="rankPoints">{{ rank_points }}</strong>
                <small>điểm xếp hạng</small>
            </div>
        </div>

        <section class="debate-lobby solo-rank-lobby">
            <article class="app-panel player-card solo-player-card">
                <div class="solo-avatar-frame">
                    <div class="solo-avatar"><i data-lucide="user"></i></div>
                    <div class="solo-wreath"></div>
                </div>
                <h2>Người chơi</h2>
                <p class="solo-rank-name">{{ rank.name }}</p>
                <div class="rank-track" aria-label="Các bậc xếp hạng">
                    {% for rank_item in ranks %}
                    <span class="rank-token {% if rank_item.name == rank.name %}active{% endif %}">{{ rank_item.name }}</span>
                    {% endfor %}
                </div>
            </article>

            <article class="app-panel match-card solo-match-card">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Sảnh chờ</p>
                        <h2>Tranh biện cá nhân</h2>
                    </div>
                </div>
                <div class="mode-toggle">
                    <button class="mode-button active" type="button" data-debate-mode="solo">
                        <i data-lucide="swords"></i>
                        <span>Tranh biện cá nhân</span>
                    </button>
                    <button class="mode-button" type="button" data-debate-mode="room">
                        <i data-lucide="users"></i>
                        <span>Phòng 5 người</span>
                    </button>
                </div>
                <button class="button primary" type="button" id="findDebateMatch" data-matching-url="{{ url_for('main.debate_matching') }}" data-room-url="{{ url_for('main.debate_room_matching') }}">
                    <i data-lucide="search"></i>
                    <span>Ghép trận</span>
                </button>
                <p class="socratic-meta" id="matchStatus"></p>
            </article>

            <article class="app-panel leaderboard-card solo-leaderboard-card">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Bảng xếp hạng</p>
                        <h2>Toàn hệ thống</h2>
                    </div>
                    <div class="leaderboard-cup"><i data-lucide="trophy"></i></div>
                </div>
                <ol class="leaderboard-list pro-leaderboard">
                    <li class="leaderboard-row champion">
                        <span class="leaderboard-place"><i data-lucide="crown"></i></span>
                        <span class="leaderboard-player">
                            <strong>Lan Anh</strong>
                            <small><span class="mini-rank diamond">Kim Cương</span></small>
                        </span>
                        <strong class="leaderboard-score">442</strong>
                    </li>
                    <li class="leaderboard-row">
                        <span class="leaderboard-place silver"><i data-lucide="medal"></i></span>
                        <span class="leaderboard-player">
                            <strong>Minh Quân</strong>
                            <small><span class="mini-rank gold">Vàng</span></small>
                        </span>
                        <strong class="leaderboard-score">388</strong>
                    </li>
                    <li class="leaderboard-row">
                        <span class="leaderboard-place bronze"><i data-lucide="medal"></i></span>
                        <span class="leaderboard-player">
                            <strong>Bảo Trâm</strong>
                            <small><span class="mini-rank gold">Vàng</span></small>
                        </span>
                        <strong class="leaderboard-score">315</strong>
                    </li>
                    <li class="leaderboard-row self">
                        <span class="leaderboard-place"><i data-lucide="shield"></i></span>
                        <span class="leaderboard-player">
                            <strong>Bạn</strong>
                            <small><span class="mini-rank current">{{ rank.name }}</span></small>
                        </span>
                        <strong class="leaderboard-score" id="leaderboardSelf">{{ rank_points }}</strong>
                    </li>
                </ol>
            </article>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_battle.html

```html
{% extends "base.html" %}

{% block title %}Trận Tranh biện cá nhân · Đấu trường lập luận{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Rời trận</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <section class="debate-arena solo-battle-page" id="debateArena" data-topic-index="{{ topic_index }}">
            <div class="debate-topic">
                <p class="eyebrow dark">Tranh biện cá nhân · Chủ đề tranh biện</p>
                <h1 id="debateTopic">{{ topic.title }}</h1>
                <div class="topic-sides">
                    <span id="debateSideA">{{ topic.side_a }}</span>
                    <span id="debateSideB">{{ topic.side_b }}</span>
                </div>
            </div>

            <div class="debate-board">
                <article class="debate-speaker active">
                    <div class="speaker-head">
                        <span>Hiệp 1 · Lập luận của bạn</span>
                        <strong id="debateTimer">30s</strong>
                    </div>
                    <div class="argument-skill-row">
                        <span>Bằng chứng</span>
                        <span>Phản ví dụ</span>
                        <span>Bắt lỗi ngụy biện</span>
                        <span>Tái lập luận</span>
                    </div>
                    <div class="voice-control-row">
                        <button class="voice-button" type="button" id="voiceArgumentButton" aria-pressed="false">
                            <i data-lucide="mic"></i>
                            <span>Nói lập luận</span>
                        </button>
                        <span class="voice-status" id="voiceArgumentStatus">Nhận giọng nói tiếng Việt</span>
                    </div>
                    <textarea id="playerArgument" rows="8" placeholder="Viết đòn lập luận của bạn: nêu quan điểm, lý do, bằng chứng và dự đoán phản biện..."></textarea>
                    <button class="button primary" type="button" id="finishDebateTurn">
                        <i data-lucide="check"></i>
                        <span>Tung đòn</span>
                    </button>
                    <p class="socratic-meta battle-status" id="battleStatus"></p>
                </article>

                <article class="debate-speaker opponent">
                    <div class="speaker-head">
                        <span>Đối thủ AI</span>
                        <strong>Phản công</strong>
                    </div>
                    <div class="opponent-transcript" id="opponentTranscript"></div>
                </article>
            </div>
        </section>

        <section class="app-panel debate-result" id="debateResult" hidden>
            <div class="panel-heading">
                <div>
                    <p class="eyebrow dark">Kết quả trận</p>
                    <h2 id="debateWinner">Đang chấm...</h2>
                </div>
                <span class="response-meta" id="debateScoreMeta"></span>
            </div>
            <p id="debateFeedback"></p>
            <div class="rubric-grid" id="debateRubric"></div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_matching.html

```html
{% extends "base.html" %}

{% block title %}Ghép trận Tranh biện cá nhân · AI Critical Thinking Lab{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Thoát</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content solo-stage-content">
        <section class="solo-match-page" aria-live="polite">
            <div class="solo-match-dialog">
                <a class="solo-close" href="{{ url_for('main.module_detail', slug=module.slug) }}" aria-label="Hủy ghép trận"><i data-lucide="x"></i></a>
                <div class="solo-countdown-ring">
                    <span id="matchCountdown">23</span>
                </div>
                <p class="eyebrow dark">Tranh biện cá nhân</p>
                <h1 id="matchmakingTitle">Đang ghép đối thủ</h1>
                <p id="matchmakingHint">Hệ thống đang tìm Đối thủ AI cùng cấp lập luận.</p>
                <div class="solo-match-actions">
                    <a class="button primary" id="readyDebateMatch" data-vs-url="{{ url_for('main.debate_vs', topic=topic_index) }}" href="{{ url_for('main.debate_vs', topic=topic_index) }}">Sẵn sàng</a>
                    <a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">Hủy</a>
                </div>
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_result_page.html

```html
{% extends "base.html" %}

{% block title %}Kết quả Tranh biện cá nhân · Đấu trường lập luận{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Sảnh</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content solo-result-content">
        <section class="solo-result-hero {{ result.winner }}">
            <p class="eyebrow dark">Kết quả Tranh biện cá nhân</p>
            <h1>
                {% if result.get('provisional') %}
                Đang chờ đánh giá
                {% elif result.winner == "player" %}
                Bạn đã thắng
                {% elif result.winner == "draw" %}
                Trận hòa
                {% else %}
                Bạn đã thua
                {% endif %}
            </h1>
            <div class="result-scoreline">
                <span>Bạn <strong>{{ 'Chờ đánh giá' if result.get('provisional') else result.player.total }}</strong></span>
                <em>Đối đầu</em>
                <span>Đối thủ <strong>{{ 'Chờ đánh giá' if result.get('provisional') else result.opponent.total }}</strong></span>
            </div>
            <div class="rank-delta {% if result.rank_delta > 0 %}gain{% elif result.rank_delta < 0 %}loss{% else %}safe{% endif %}">
                {% if result.rank_delta > 0 %}+{% endif %}{{ result.rank_delta }} điểm xếp hạng
            </div>
            {% if result.previous_rank.name != result.rank.name %}
            <div class="promotion-burst">Lên hạng: {{ result.rank.name }}</div>
            {% endif %}
        </section>

        <section class="solo-result-grid">
            <article class="app-panel rank-result-card">
                <div class="solo-avatar-frame">
                    <div class="solo-avatar"><i data-lucide="user"></i></div>
                    <div class="solo-wreath"></div>
                </div>
                <p class="eyebrow dark">Rank hiện tại</p>
                <h2>{{ result.rank.name }}</h2>
                <strong class="rank-total">{{ result.rank_points }}</strong>
                <div class="rank-progress">
                    <span style="width: {{ rank_progress }}%"></span>
                </div>
                <p class="rank-next">
                    {% if next_rank %}
                    Còn {{ next_rank.min - result.rank_points }} điểm để lên {{ next_rank.name }}
                    {% else %}
                    Bạn đang ở bậc cao nhất
                    {% endif %}
                </p>
            </article>

            <article class="app-panel rank-ladder-card">
                <p class="eyebrow dark">Bậc xếp hạng</p>
                <div class="rank-ladder">
                    {% for rank_item in ranks %}
                    <div class="rank-step {% if result.rank_points >= rank_item.min %}unlocked{% endif %} {% if rank_item.name == result.rank.name %}current{% endif %}">
                        <span>{{ rank_item.name }}</span>
                        <strong>{{ rank_item.min }}</strong>
                    </div>
                    {% endfor %}
                </div>
                <p class="rank-rule">Thắng +20 điểm. Thua -30 điểm từ Vàng trở lên. Đồng và Bạc thua không trừ điểm.</p>
            </article>
        </section>

        <section class="app-panel debate-result-detail">
            <div class="panel-heading">
                <div>
                    <p class="eyebrow dark">Phân tích trận</p>
                    <h2>Điểm mạnh và điểm cần sửa</h2>
                </div>
            </div>
            <p>{{ result.feedback }}</p>
            <div class="rubric-grid">
                {% for item in result.rubric_scores %}
                <article class="rubric-item">
                    <span>{{ item.label }}</span>
                    <strong>{{ item.score }}/{{ item.max }}</strong>
                    <p>{{ item.get('status', '') }} · {{ item.get('feedback', '') }}</p>
                </article>
                {% endfor %}
            </div>
            <div class="solo-result-actions">
                <a class="button primary" href="{{ url_for('main.debate_matching') }}"><i data-lucide="rotate-cw"></i><span>Đấu tiếp</span></a>
                <a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">Về sảnh</a>
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_room_battle.html

```html
{% extends "base.html" %}

{% block title %}Phòng tranh luận 5 người · Đấu trường lập luận{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Rời phòng</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content room-battle-content">
        <section class="room-topic-hero">
            <p class="eyebrow dark">Phòng tranh luận 5 người</p>
            <h1>{{ topic.title }}</h1>
            <div class="room-battle-meta">
                <span><i data-lucide="timer"></i> 4 vòng</span>
                <span><i data-lucide="users"></i> 5 vai trò</span>
                <span><i data-lucide="scale"></i> AI trọng tài chấm cuối trận</span>
            </div>
        </section>

        <section class="room-arena">
            <div class="room-team team-blue">
                <div class="team-heading">
                    <span>Đội Ủng hộ</span>
                    <strong>{{ topic.side_a }}</strong>
                </div>
                <article class="room-player-card active" data-room-player="0">
                    <div class="room-player-avatar"><i data-lucide="user"></i></div>
                    <strong>Bạn</strong>
                    <small>Mở luận điểm</small>
                    <em>Sẵn sàng</em>
                </article>
                <article class="room-player-card" data-room-player="1">
                    <div class="room-player-avatar bot"><i data-lucide="bot"></i></div>
                    <strong>AI Minh</strong>
                    <small>Đưa bằng chứng</small>
                    <em>Sẵn sàng</em>
                </article>
            </div>

            <div class="room-center-stage">
                <div class="room-phase-board">
                    <p class="eyebrow dark" id="roomPhaseLabel">Vòng 1 · Mở luận điểm</p>
                    <h2 id="roomTurnSpeaker">Lượt của Bạn</h2>
                    <span id="roomTurnRole">Mở luận điểm cho đội Ủng hộ</span>
                </div>
                <div class="room-transcript" id="roomTranscript">
                    <article>
                        <strong>AI Trọng tài</strong>
                        <p>Phòng đã bắt đầu. Mỗi người nói đúng vai trò, tập trung vào bằng chứng và phản biện.</p>
                    </article>
                </div>
                <form class="room-speech-panel" id="roomDebateForm">
                    <textarea id="roomDebateInput" rows="4" placeholder="Nhập phần phát biểu của bạn trong lượt này..."></textarea>
                    <button class="button primary" type="submit"><i data-lucide="send"></i><span>Gửi lượt</span></button>
                    <p class="socratic-meta" id="roomBattleStatus"></p>
                </form>
            </div>

            <div class="room-team team-red">
                <div class="team-heading">
                    <span>Đội Phản đối</span>
                    <strong>{{ topic.side_b }}</strong>
                </div>
                <article class="room-player-card" data-room-player="2">
                    <div class="room-player-avatar bot"><i data-lucide="bot"></i></div>
                    <strong>AI Trâm</strong>
                    <small>Phản biện</small>
                    <em>Sẵn sàng</em>
                </article>
                <article class="room-player-card" data-room-player="3">
                    <div class="room-player-avatar bot"><i data-lucide="bot"></i></div>
                    <strong>AI Quân</strong>
                    <small>Bắt lỗi ngụy biện</small>
                    <em>Sẵn sàng</em>
                </article>
            </div>

            <article class="room-observer-card" data-room-player="4">
                <div class="room-player-avatar judge"><i data-lucide="gavel"></i></div>
                <div>
                    <strong>AI Lan</strong>
                    <small>Tổng kết viên · ghi lại điểm mạnh/yếu của hai đội</small>
                </div>
                <em>Quan sát</em>
            </article>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_room_matching.html

```html
{% extends "base.html" %}

{% block title %}Ghép phòng 5 người · Đấu trường lập luận{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Thoát</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content solo-stage-content">
        <section class="room-match-page">
            <div class="room-match-header">
                <p class="eyebrow dark">Phòng 5 người</p>
                <h1 id="roomTitle">Đang tìm người chơi</h1>
                <div class="room-countdown">
                    <span id="roomCountdown">18</span>
                    <small>giây</small>
                </div>
                <p id="roomStatus">Đã có 1/5 người trong phòng. Đang tìm thêm người chơi...</p>
            </div>

            <div class="room-slots">
                <article class="room-slot filled self" data-room-slot>
                    <div class="room-slot-avatar"><i data-lucide="user"></i></div>
                    <strong>Bạn</strong>
                    <small>Chủ phòng</small>
                </article>
                <article class="room-slot" data-room-slot>
                    <div class="room-slot-avatar"><i data-lucide="loader"></i></div>
                    <strong>Đang tìm...</strong>
                    <small>Chờ người chơi</small>
                </article>
                <article class="room-slot" data-room-slot>
                    <div class="room-slot-avatar"><i data-lucide="loader"></i></div>
                    <strong>Đang tìm...</strong>
                    <small>Chờ người chơi</small>
                </article>
                <article class="room-slot" data-room-slot>
                    <div class="room-slot-avatar"><i data-lucide="loader"></i></div>
                    <strong>Đang tìm...</strong>
                    <small>Chờ người chơi</small>
                </article>
                <article class="room-slot" data-room-slot>
                    <div class="room-slot-avatar"><i data-lucide="loader"></i></div>
                    <strong>Đang tìm...</strong>
                    <small>Chờ người chơi</small>
                </article>
            </div>

            <div class="room-match-actions">
                <a class="button secondary" href="{{ url_for('main.module_detail', slug=module.slug) }}">Hủy</a>
                <button class="button primary" type="button" id="roomReadyButton" data-room-battle-url="{{ url_for('main.debate_room_battle', topic=topic_index) }}" disabled>
                    <i data-lucide="check"></i>
                    <span>Sẵn sàng</span>
                </button>
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/debate_vs.html

```html
{% extends "base.html" %}

{% block title %}VS · Đấu trường lập luận{% endblock %}

{% block body_class %}game-page{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.module_detail', slug=module.slug) }}"><i data-lucide="arrow-left"></i><span>Thoát</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content solo-stage-content">
        <section class="solo-vs-screen solo-vs-page" id="soloVsScreen" data-battle-url="{{ url_for('main.debate_battle', topic=topic_index) }}">
            <article class="vs-player blue">
                <div class="solo-avatar-frame">
                    <div class="solo-avatar"><i data-lucide="user"></i></div>
                    <div class="solo-wreath"></div>
                </div>
                <strong>Bạn</strong>
                <span>{{ rank.name }} · <span id="soloSelfPoints">{{ rank_points }}</span> điểm</span>
            </article>
            <div class="vs-center">
                <div class="vs-mark">Đối đầu</div>
                <span id="vsCountdown">3</span>
            </div>
            <article class="vs-player red">
                <div class="solo-avatar-frame">
                    <div class="solo-avatar bot"><i data-lucide="bot"></i></div>
                    <div class="solo-wreath"></div>
                </div>
                <strong>Đối thủ AI</strong>
                <span>Cùng cấp · phản biện mạnh</span>
            </article>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/detective_fields.html

```html
{% extends "base.html" %}

{% block title %}Chọn lĩnh vực Thám tử AI · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content assignment-list-page">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
        </div>

        <section class="assignment-task-grid" aria-label="Danh sách lĩnh vực Thám tử AI">
            {% if fields %}
                {% for field in fields %}
                <a class="assignment-task-box" href="{{ url_for('main.module_detail', slug=module.slug, field=field.key) }}">
                    <span class="assignment-task-icon"><i data-lucide="search-check"></i></span>
                    <strong>{{ field.name }}</strong>
                    <em>{{ field.count }} vụ án</em>
                    <span class="assignment-task-action">Vào phá án <i data-lucide="arrow-right"></i></span>
                </a>
                {% endfor %}
            {% else %}
                <article class="app-panel assignment-empty">
                    <i data-lucide="search-check"></i>
                    <h2>Chưa có lĩnh vực đang mở</h2>
                </article>
            {% endif %}
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/gemini_lab.html

```html
{% extends "base.html" %}

{% block title %}Kiểm tra kết nối AI · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell admin-shell">
    <aside class="app-sidebar" aria-label="Điều hướng quản trị">
        <a class="sidebar-item" href="{{ url_for('main.admin_dashboard') }}"><i data-lucide="shield"></i><span>Quản trị</span></a>
        <a class="sidebar-item" href="{{ url_for('main.admin_dashboard') }}#teacherAccounts"><i data-lucide="users"></i><span>Giáo viên</span></a>
        <a class="sidebar-item active" aria-current="page" href="{{ url_for('main.gemini_lab') }}"><i data-lucide="settings"></i><span>Cấu hình hệ thống</span></a>
        <a class="sidebar-item" href="{{ url_for('main.health') }}"><i data-lucide="activity"></i><span>Tình trạng hệ thống</span></a>
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">Cấu hình hệ thống</p>
                <h1>Kiểm tra kết nối Gemini</h1>
            </div>
            <button class="button primary" type="button" id="refreshGeminiStatus">
                <i data-lucide="refresh-cw"></i>
                <span>Làm mới trạng thái</span>
            </button>
        </div>

        <nav class="ui-role-tabs" aria-label="Cấu hình hệ thống"><a class="ui-back" aria-current="page" href="#geminiTestForm">Kết nối Gemini</a></nav><p class="ui-help">Khóa API dùng để xác thực với dịch vụ AI. Trạng thái cấu hình hiển thị bên dưới.</p><div class="gemini-grid">
            <section class="app-panel">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Prompt thử nghiệm</p>
                        <h2>Gửi câu hỏi thử nghiệm</h2>
                    </div>
                </div>
                <form class="gemini-form" id="geminiTestForm">
                    <textarea id="geminiPrompt" rows="8">Viết 3 câu hỏi Socratic để học sinh tự kiểm chứng một câu trả lời của AI.</textarea>
                    <button class="button primary" type="submit">
                        <i data-lucide="send"></i>
                        <span>Gửi Gemini</span>
                    </button>
                </form>
            </section>

            <section class="app-panel">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Khóa kết nối API</p>
                        <h2>Trạng thái</h2>
                    </div>
                </div>
                <div class="key-status-list" id="geminiStatus">
                    <p class="muted-note">Đang tải...</p>
                </div>
            </section>
        </div>

        <section class="app-panel">
            <div class="panel-heading">
                <div>
                    <p class="eyebrow dark">Kết quả</p>
                    <h2>Phản hồi từ Gemini</h2>
                </div>
                <span class="response-meta" id="geminiMeta"></span>
            </div>
            <pre class="gemini-output" id="geminiOutput"></pre>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/human_first.html

```html
{% extends "base.html" %}

{% block title %}Con người trước - AI sau · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}">
            <i data-lucide="arrow-left"></i>
            <span>Quay lại</span>
        </a>
        {% for item in modules %}
        <a class="sidebar-item {% if item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=item.slug) }}">
            <i data-lucide="{{ item.icon }}"></i>
            <span>{{ item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero human-first-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <a class="button primary" href="{{ url_for('main.module_detail', slug='nhat-ky-phan-tu-ai') }}">
                <i data-lucide="book-open-check"></i>
                <span>Viết phản tư</span>
            </a>
        </div>

        <section class="human-flow">
            <div class="flow-step active" data-human-step="1">
                <span>1</span>
                <strong>Em trả lời trước</strong>
            </div>
            <div class="flow-step" data-human-step="2">
                <span>2</span>
                <strong>Xem AI</strong>
            </div>
            <div class="flow-step" data-human-step="3">
                <span>3</span>
                <strong>Giữ hay đổi</strong>
            </div>
        </section>

        <section class="human-first-grid">
            <form class="app-panel human-answer-panel" id="humanFirstForm">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Bước 1</p>
                        <h2>Câu trả lời của em</h2>
                    </div>
                </div>

                <label class="field-label" for="humanQuestion">Câu hỏi</label>
                <select id="humanQuestion">
                    {% for question in questions %}
                    <option value="{{ question.id }}" data-hint="{{ question.hint }}">{{ question.subject }} · {{ question.question }}</option>
                    {% endfor %}
                </select>
                <p class="hint-text" id="humanQuestionHint" hidden>{{ questions[0].hint }}</p>

                <label class="field-label" for="humanAnswer">Trả lời trước khi xem AI</label>
                <textarea id="humanAnswer" rows="8" placeholder="Nhập câu trả lời..."></textarea>

                <div class="confidence-row">
                    <label for="humanConfidence">Mức độ chắc chắn</label>
                    <strong><span id="humanConfidenceValue">50</span>%</strong>
                </div>
                <input id="humanConfidence" type="range" min="0" max="100" value="50">

                <button class="button primary" type="submit">
                    <i data-lucide="lock-open"></i>
                    <span>Nộp & mở AI</span>
                </button>
                <p class="socratic-meta" id="humanFirstMeta"></p>
            </form>

            <section class="app-panel ai-after-panel locked" id="aiAfterPanel">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Bước 2</p>
                        <h2>Câu trả lời AI</h2>
                    </div>
                    <span class="response-meta" id="humanAiMeta"></span>
                </div>
                <div class="locked-state" id="aiLockedState">
                    <i data-lucide="lock"></i>
                    <p>AI đang khóa.</p>
                </div>
                <div class="ai-answer-output" id="humanAiAnswer" hidden></div>
            </section>
        </section>

        <section class="app-panel decision-panel" id="humanDecisionPanel" hidden>
            <div class="panel-heading">
                <div>
                    <p class="eyebrow dark">Bước 3</p>
                    <h2>Em giữ hay đổi câu trả lời?</h2>
                </div>
            </div>
            <div class="decision-actions">
                <button class="decision-button active" type="button" data-decision="keep">
                    <i data-lucide="shield-check"></i>
                    <span>Giữ câu trả lời của em</span>
                </button>
                <button class="decision-button" type="button" data-decision="change">
                    <i data-lucide="refresh-cw"></i>
                    <span>Đổi theo AI</span>
                </button>
            </div>
            <label class="field-label" for="decisionReason">Lý do</label>
            <textarea id="decisionReason" rows="4" placeholder="Nhập lý do..."></textarea>
            <a class="button primary" id="goReflectionLink" href="{{ url_for('main.module_detail', slug='nhat-ky-phan-tu-ai') }}">
                <i data-lucide="book-open-check"></i>
                <span>Hoàn thành & phản tư</span>
            </a>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/intentional_error.html

```html
{% extends "base.html" %}

{% block title %}AI cố tình sai · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
        </div>

        <section class="level-picker" aria-label="Chọn cấp độ lỗi">
            {% for level in levels %}
            <button class="level-button {% if level.level == item.level %}active{% endif %}" type="button" data-error-level="{{ level.level }}">
                <span>{{ level.level }}</span>
                <small>{{ level.level_name }}</small>
            </button>
            {% endfor %}
        </section>

        <section class="error-layout">
            <article class="app-panel error-task" id="errorTask" data-level="{{ item.level }}">
                <p class="eyebrow dark">Nhiệm vụ</p>
                <h2 id="errorQuestion">{{ item.question }}</h2>
                <div class="ai-answer-box selectable" id="errorAiAnswer">{{ item.ai_answer }}</div>
            </article>

            <form class="app-panel error-form" id="errorForm">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Phân tích lỗi</p>
                        <h2>Kiểm chứng</h2>
                    </div>
                    <span class="response-meta" id="errorMeta"></span>
                </div>
                <label class="field-label" for="errorSuspicious">Đoạn đáng nghi</label>
                <textarea id="errorSuspicious" rows="2"></textarea>
                <label class="field-label" for="errorType">Loại lỗi</label>
                <select id="errorType">
                    <option>Dữ kiện sai</option>
                    <option>Nguồn không tồn tại</option>
                    <option>Suy luận thiếu căn cứ</option>
                    <option>Khái quát hóa quá mức</option>
                    <option>Đúng nhưng sai bối cảnh</option>
                    <option>Thiên lệch</option>
                    <option>Khái quát hóa + thiên lệch</option>
                </select>
                <label class="field-label" for="errorExplanation">Vì sao đáng nghi?</label>
                <textarea id="errorExplanation" rows="3"></textarea>
                <label class="field-label" for="errorEvidence">Nguồn/bằng chứng kiểm chứng</label>
                <textarea id="errorEvidence" rows="3"></textarea>
                <label class="field-label" for="errorRewrite">Viết lại chính xác hơn</label>
                <textarea id="errorRewrite" rows="4"></textarea>
                <button class="button primary" type="submit"><i data-lucide="check"></i><span>Chấm bài</span></button>
            </form>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/login.html

```html
{% extends "base.html" %}

{% block title %}Đăng nhập · AI Critical Thinking Lab{% endblock %}

{% block content %}
<section class="auth-page">
    <form class="auth-card" method="post">
        <p class="eyebrow dark">Đăng nhập</p>
        <h1>Tiếp tục hành trình học tập</h1>
        <p>Chọn vai trò và đăng nhập để vào không gian của bạn.</p>
        {% if error %}<div class="auth-error">{{ error }}</div>{% endif %}

        <label class="field-label" for="role">Đăng nhập với tư cách</label>
        <select id="role" name="role">
            <option value="student" {% if selected_role == "student" %}selected{% endif %}>Học sinh</option>
            <option value="teacher" {% if selected_role == "teacher" %}selected{% endif %}>Giáo viên</option>
            <option value="admin" {% if selected_role == "admin" %}selected{% endif %}>Quản trị</option>
        </select>

        <label class="field-label" for="username">Tên đăng nhập</label>
        <input id="username" name="username" autocomplete="username" required>

        <label class="field-label" for="password">Mật khẩu</label>
        <div class="password-field">
            <input id="password" name="password" type="password" autocomplete="current-password" required>
            <button type="button" class="password-toggle" data-password-toggle="password" aria-label="Hiện mật khẩu"><i data-lucide="eye"></i></button>
        </div>

        <button class="button primary" type="submit"><i data-lucide="log-in"></i><span>Đăng nhập</span></button>
        <div class="auth-links">
            <a class="text-link" href="{{ url_for('main.student_register') }}">Tạo tài khoản học sinh</a>
            <a class="text-link" href="{{ url_for('main.landing') }}">Quay lại trang chủ</a>
        </div>
    </form>
</section>
{% endblock %}

```

## app/templates/pages/module_detail.html

```html
{% extends "base.html" %}

{% block title %}{{ module.title }} · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}">
            <i data-lucide="arrow-left"></i>
            <span>Quay lại</span>
        </a>
        {% for item in modules %}
        <a class="sidebar-item {% if item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=item.slug) }}">
            <i data-lucide="{{ item.icon }}"></i>
            <span>{{ item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <div class="module-status-card">
                <span>{{ module.status }}</span>
                <strong>{{ module.progress }}%</strong>
                <div class="progress-track">
                    <span style="width: {{ module.progress }}%"></span>
                </div>
            </div>
        </div>

        <section class="activity-frame">
            <div class="activity-toolbar">
                <button type="button" title="Làm mới"><i data-lucide="refresh-cw"></i></button>
                <button type="button" title="Lưu"><i data-lucide="save"></i></button>
                <button type="button" title="Mở rộng"><i data-lucide="maximize-2"></i></button>
            </div>
            <div class="activity-placeholder">
                <i data-lucide="{{ module.icon }}"></i>
                <h2>{{ module.title }}</h2>
                <a class="button primary" href="{{ url_for('main.app_home') }}">
                    <i data-lucide="grid-3x3"></i>
                    <span>Chọn mô-đun khác</span>
                </a>
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/reflection_journal.html

```html
{% extends "base.html" %}

{% block title %}Nhật ký phản tư AI · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}">
            <i data-lucide="arrow-left"></i>
            <span>Quay lại</span>
        </a>
        {% for item in modules %}
        <a class="sidebar-item {% if item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=item.slug) }}">
            <i data-lucide="{{ item.icon }}"></i>
            <span>{{ item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <a class="button primary" href="{{ url_for('main.module_detail', slug='chatbot-socratic') }}">
                <i data-lucide="messages-square"></i>
                <span>Vào chatbot</span>
            </a>
        </div>

        <div class="reflection-grid">
            <form class="app-panel reflection-form" id="reflectionForm">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Phản tư sau phiên học</p>
                        <h2>Nhật ký 3 phần</h2>
                    </div>
                    <span class="response-meta" id="reflectionMeta"></span>
                </div>
                <section class="reflection-block">
                    <div>
                        <span>01</span>
                        <h3>Tóm tắt nội dung vừa học</h3>
                    </div>
                    <p id="reflectionSummary">Chưa có phiên học nào được chuyển sang nhật ký.</p>
                </section>
                <section class="reflection-block">
                    <div>
                        <span>02</span>
                        <h3>AI nhận xét sơ bộ</h3>
                    </div>
                    <p id="reflectionAiReview">Khi kết thúc một phiên chatbot, nhận xét của AI sẽ xuất hiện ở đây.</p>
                </section>
                <section class="reflection-block reflection-takeaway">
                    <div>
                        <span>03</span>
                        <h3>Điều em tự rút ra</h3>
                    </div>
                    <textarea id="reflectionTakeaway" rows="5" placeholder="Nhập điều em rút ra..."></textarea>
                    <div class="reflection-choice-row" aria-label="Gợi ý tự phản tư">
                        <button type="button" data-takeaway-chip="Em đã đổi cách nhìn sau phiên này.">Em đổi cách nhìn</button>
                        <button type="button" data-takeaway-chip="Em cần kiểm chứng thêm bằng nguồn khác.">Cần kiểm chứng thêm</button>
                        <button type="button" data-takeaway-chip="Em giữ quan điểm nhưng đã hiểu rõ điểm yếu của lập luận.">Giữ quan điểm</button>
                    </div>
                </section>
                <button class="button primary" type="submit">
                    <i data-lucide="save"></i>
                    <span>Lưu nhật ký</span>
                </button>
            </form>

            <aside class="reflection-side">
                <section class="app-panel reflection-profile-card">
                    <div class="student-avatar-card">
                        <div class="student-avatar-preview" data-avatar-preview>
                            {% if student and student.avatar_filename %}
                            <img src="{{ url_for('main.student_avatar_file', filename=student.avatar_filename) }}" alt="Ảnh đại diện của {{ student.name }}">
                            {% else %}
                            <span>{{ (student.name if student else "Học sinh")[:1] }}</span>
                            {% endif %}
                        </div>
                        <div>
                            <p class="eyebrow dark">{{ student.username if student else "student" }}</p>
                            <h2>{{ student.name if student else "Học sinh" }}</h2>
                            {% if avatar_error %}<div class="auth-error wide">{{ avatar_error }}</div>{% endif %}
                            {% if avatar_success %}<div class="auth-success">{{ avatar_success }}</div>{% endif %}
                        </div>
                    </div>
                    <form class="avatar-form" method="post" action="{{ url_for('main.student_avatar_upload') }}" enctype="multipart/form-data">
                        <input type="hidden" name="next" value="nhat-ky-phan-tu-ai">
                        <label class="field-label" for="reflectionAvatar">Ảnh hồ sơ</label>
                        <div class="avatar-upload-row">
                            <input id="reflectionAvatar" name="avatar" type="file" accept="image/png,image/jpeg,image/gif,image/webp" data-avatar-input required>
                            <button class="button primary" type="submit"><i data-lucide="upload"></i><span>Lưu ảnh</span></button>
                        </div>
                    </form>
                </section>

                <section class="app-panel reflection-history">
                    <div class="panel-heading">
                        <div>
                            <p class="eyebrow dark">Gần đây</p>
                            <h2>Nhật ký đã lưu</h2>
                        </div>
                    </div>
                    <div id="reflectionEntries">
                        {% if entries %}
                            {% for entry in entries %}
                            <article class="reflection-entry">
                                <span>{{ entry.module }}</span>
                                <strong>{{ (entry.answers.get('takeaway') or entry.answers.get('summary') or (entry.answers|length ~ ' mục đã lưu'))|truncate(96) }}</strong>
                            </article>
                            {% endfor %}
                        {% else %}
                        <p class="muted-note">Chưa có nhật ký.</p>
                        {% endif %}
                    </div>
                </section>
            </aside>
        </div>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/skill_profile.html

```html
{% extends "base.html" %}

{% block title %}Hồ sơ năng lực · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
                {% if profile.get('has_synthetic_data') %}<p>Dữ liệu mô phỏng để kiểm tra hệ thống; không phải kết quả thực nghiệm.</p>{% endif %}
            </div>
            <a class="button primary" href="#savedActivities"><i data-lucide="save"></i><span>Hoạt động đã lưu</span></a>
        </div>

        <section class="app-panel profile-avatar-panel">
            <div class="student-avatar-card">
                <div class="student-avatar-preview" data-avatar-preview>
                    {% if student and student.avatar_filename %}
                    <img src="{{ url_for('main.student_avatar_file', filename=student.avatar_filename) }}" alt="Ảnh đại diện của {{ student.name }}">
                    {% else %}
                    <span>{{ (student.name if student else "Học sinh")[:1] }}</span>
                    {% endif %}
                </div>
                <div>
                    <p class="eyebrow dark">{{ student.username if student else "student" }}</p>
                    <h2>{{ student.name if student else "Học sinh" }}</h2>
                    {% if avatar_error %}<div class="auth-error wide">{{ avatar_error }}</div>{% endif %}
                    {% if avatar_success %}<div class="auth-success">{{ avatar_success }}</div>{% endif %}
                </div>
            </div>
            <form class="avatar-form" method="post" action="{{ url_for('main.student_avatar_upload') }}" enctype="multipart/form-data">
                <label class="field-label" for="avatar">Ảnh đại diện</label>
                <div class="avatar-upload-row">
                    <input id="avatar" name="avatar" type="file" accept="image/png,image/jpeg,image/gif,image/webp" data-avatar-input required>
                    <button class="button primary" type="submit"><i data-lucide="upload"></i><span>Lưu ảnh đại diện</span></button>
                </div>
            </form>
        </section>

        <section class="profile-grid">
            <article class="app-panel radar-panel">
                <div class="panel-heading"><div><p class="eyebrow dark">{{ profile.student_name }}</p><h2>Radar 8 năng lực</h2></div></div>
                <div class="radar-chart" id="profileRadar" data-scores="{% for skill in profile.skills %}{{ skill.score }}{% if not loop.last %},{% endif %}{% endfor %}">
                    <svg viewBox="0 0 320 320" role="img" aria-label="Biểu đồ radar năng lực"></svg>
                </div>
            </article>

            <article class="app-panel profile-skills">
                <div class="panel-heading"><div><p class="eyebrow dark">Chi tiết</p><h2>Điểm từng năng lực</h2></div></div>
                <div class="skill-bars">
                    {% for skill in profile.skills %}
                    <div class="skill-row">
                        <span>{{ skill.label }}</span>
                        <strong>{{ skill.score }}</strong>
                        <div class="progress-track"><span style="width: {{ skill.score }}%"></span></div>
                    </div>
                    {% endfor %}
                </div>
            </article>
        </section>

        <section class="profile-grid lower">
            <article class="app-panel progress-panel">
                <div class="panel-heading"><div><p class="eyebrow dark">Tiến bộ</p><h2>7 phiên gần nhất</h2></div></div>
                <div class="line-chart" data-values="{% for value in profile.timeline %}{{ value }}{% if not loop.last %},{% endif %}{% endfor %}" id="profileLine"></div>
            </article>

            <article class="app-panel">
                <div class="panel-heading"><div><p class="eyebrow dark">Khuyến nghị</p><h2>Nhiệm vụ tiếp theo</h2></div></div>
                <div class="recommendation-list">
                    {% for item in profile.recommendations %}
                    <article><strong>{{ item.module }}</strong><span>{{ item.reason }}</span></article>
                    {% endfor %}
                </div>
            </article>
        </section>

        <section class="app-panel">
            <div class="panel-heading"><div><p class="eyebrow dark">Lỗi thường gặp</p><h2>Mẫu cần chú ý</h2></div></div>
            <div class="common-error-list">
                {% for error in profile.common_errors %}
                <article><i data-lucide="alert-circle"></i><span>{{ error }}</span></article>
                {% endfor %}
            </div>
        </section>

        <section class="app-panel" id="savedActivities">
            <div class="panel-heading"><div><p class="eyebrow dark">Đã lưu</p><h2>Hoạt động gần đây</h2></div></div>
            <div class="report-list">
                {% if activities %}
                    {% for activity in activities %}
                    <article>
                        <span>{{ activity.created_at[:10] }}{% if activity.get('synthetic') %} · Mô phỏng{% endif %}</span>
                        <strong>{{ activity.module }} · {{ activity.action }}</strong>
                        <p>{% if activity.score is not none %}Điểm: {{ activity.score }}{% else %}Đã lưu bài làm.{% endif %}</p>
                        {% if activity.get('synthetic') %}
                        {% set payload = activity.get('payload', {}) %}
                        <details>
                            <summary>Xem bài làm và nhận xét mô phỏng</summary>
                            <p>{{ payload.get('title', '') }}</p>
                            {% for key, label in [('answer', 'Bài làm'), ('selected', 'Lựa chọn'), ('criteria', 'Lý do'), ('synthesis', 'Tổng hợp'), ('suspicious_text', 'Chi tiết đáng nghi'), ('error_type', 'Loại lỗi'), ('explanation', 'Giải thích'), ('evidence', 'Bằng chứng'), ('rewrite', 'Viết lại')] %}
                            {% if payload.get('work', {}).get(key) %}<p><strong>{{ label }}:</strong> {{ payload.work[key] }}</p>{% endif %}
                            {% endfor %}
                            {% for placement in payload.get('work', {}).get('placements', []) %}<p>{{ placement.piece_text }} → {{ placement.bucket_label }}</p>{% endfor %}
                            {% if payload.get('prompt') %}<p>{{ payload.prompt }}</p>{% endif %}
                            {% if payload.get('assessment') %}<p>{{ payload.assessment.feedback }}</p>{% endif %}
                            {% for message in payload.get('messages', []) %}<p><strong>{{ 'HS' if message.role == 'student' else 'AI mô phỏng' }}:</strong> {{ message.content }}</p>{% endfor %}
                            {% if activity.action == 'reflection' %}<p>{{ payload.get('answers', {}).get('takeaway', '') }}</p>{% endif %}
                        </details>
                        {% endif %}
                    </article>
                    {% endfor %}
                {% else %}
                    <p class="muted-note">Chưa có hoạt động.</p>
                {% endif %}
            </div>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/socratic_chat.html

```html
{% extends "base.html" %}

{% block title %}Chatbot Socratic · AI Critical Thinking Lab{% endblock %}

{% block content %}
{% set stage_icons = {
    "PROBE": "ti-help-circle",
    "CLAIM": "ti-bulb",
    "EVIDENCE": "ti-file-check",
    "COUNTER": "ti-swords",
    "REVISE": "ti-refresh",
    "SYNTHESIZE": "ti-stack-2"
} %}
{% set board_icons = {
    "claims": "ti-bulb",
    "evidence": "ti-file-check",
    "unclear": "ti-question-mark",
    "counterpoints": "ti-message-question",
    "revisions": "ti-edit"
} %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}">
            <i data-lucide="arrow-left"></i>
            <span>Quay lại</span>
        </a>
        {% for item in modules %}
        <a class="sidebar-item {% if item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=item.slug) }}">
            <i data-lucide="{{ item.icon }}"></i>
            <span>{{ item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content socratic-page">
        <div class="module-detail-hero socratic-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <a class="button primary" href="{{ url_for('main.module_detail', slug='nhat-ky-phan-tu-ai') }}" id="finishSocraticLink">
                <i class="ti ti-book-2"></i>
                <span>Kết thúc & Phản tư</span>
            </a>
        </div>

        <section class="socratic-stagebar" aria-label="Tiến trình Socratic">
            {% for stage in stages %}
            <button class="stage-pill stage-{{ stage.key|lower }} {% if loop.index0 == 0 %}active{% endif %}" type="button" data-stage-index="{{ loop.index0 }}">
                <span><i class="ti {{ stage_icons.get(stage.key, 'ti-circle') }}"></i>{{ stage.key }}</span>
                <small>{{ stage.label }}</small>
            </button>
            {% endfor %}
        </section>

        <section class="socratic-workspace">
            <div class="socratic-chat-panel">
                <div class="socratic-mode-switch" aria-label="Chọn phiên bản chatbot">
                    <button class="socratic-mode-button active" type="button" data-socratic-mode="easy">
                        <i data-lucide="hand-heart"></i>
                        <span>Dễ tiếp cận</span>
                    </button>
                    <button class="socratic-mode-button" type="button" data-socratic-mode="advanced">
                        <i data-lucide="brain-circuit"></i>
                        <span>Nâng cao</span>
                    </button>
                </div>
                <div class="chat-thread" id="socraticThread" aria-live="polite">
                    <article class="socratic-message ai">
                        <span>AI</span>
                        <p>Em nêu một chủ đề hoặc câu hỏi. Mình sẽ gợi ý từng bước để em tự viết được câu trả lời.</p>
                    </article>
                </div>
                <form class="socratic-form" id="socraticForm">
                    <textarea id="socraticInput" rows="3" placeholder="Nhập câu hỏi..."></textarea>
                    <button class="button primary" type="submit">
                        <i class="ti ti-send"></i>
                        <span>Gửi</span>
                    </button>
                </form>
                <p class="socratic-meta" id="socraticMeta"></p>
            </div>

            <aside class="thinking-board" aria-label="Bảng tư duy">
                <div class="panel-heading">
                    <div>
                        <p class="eyebrow dark">Bảng tư duy</p>
                        <h2>Lập luận đang hình thành</h2>
                    </div>
                </div>
                <div class="board-columns">
                    {% for key, label in board_keys.items() %}
                    <section class="board-section" data-board-key="{{ key }}">
                        <h3><i class="ti {{ board_icons.get(key, 'ti-circle') }}"></i><span>{{ label }}</span></h3>
                        <div class="board-items"></div>
                    </section>
                    {% endfor %}
                </div>
            </aside>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/student_register.html

```html
{% extends "base.html" %}

{% block title %}Đăng ký học sinh · AI Critical Thinking Lab{% endblock %}

{% block content %}
<section class="auth-page">
    <form class="auth-card" method="post">
        <p class="eyebrow dark">Học sinh</p>
        <h1>Tạo tài khoản học tập</h1>
        {% if error %}<div class="auth-error">{{ error }}</div>{% endif %}

        <fieldset class="ui-fieldset"><legend>Thông tin cá nhân</legend>
        <label class="field-label" for="name">Tên hiển thị</label>
        <input id="name" name="name" autocomplete="name" placeholder="Tên của em">

        </fieldset><fieldset class="ui-fieldset"><legend>Lớp và giáo viên</legend>
        <label class="field-label" for="school">Trường</label>
        <input id="school" name="school" required maxlength="150" value="{{ request.form.get('school', '') }}">
        <label class="field-label" for="class_name">Lớp</label>
        <input id="class_name" name="class_name" required maxlength="60" value="{{ request.form.get('class_name', '') }}">
        <label class="field-label" for="teacher_username">Giáo viên phụ trách</label>
        <select id="teacher_username" name="teacher_username" required><option value="">Chọn giáo viên</option>{% for t in teachers if t.active %}<option value="{{ t.username }}">{{ t.name }} ({{ t.username }})</option>{% endfor %}</select>
        </fieldset><fieldset class="ui-fieldset"><legend>Tài khoản đăng nhập</legend>
        <label class="field-label" for="username">Tên đăng nhập</label>
        <input id="username" name="username" autocomplete="username" required>

        <label class="field-label" for="password">Mật khẩu</label>
        <div class="password-field">
            <input id="password" name="password" type="password" autocomplete="new-password" required>
            <button type="button" class="password-toggle" data-password-toggle="password" aria-label="Hiện mật khẩu"><i data-lucide="eye"></i></button>
        </div>

        <p class="ui-help">Ghi nhớ tên đăng nhập và giữ mật khẩu riêng tư.</p></fieldset>
        <button class="button primary" type="submit"><i data-lucide="user-plus"></i><span>Tạo tài khoản</span></button>
        <div class="auth-links">
            <a class="text-link" href="{{ url_for('main.login', role='student') }}">Đã có tài khoản</a>
            <a class="text-link" href="{{ url_for('main.landing') }}">Quay lại trang chủ</a>
        </div>
    </form>
</section>
{% endblock %}

```

## app/templates/pages/teacher_dashboard.html

```html
{% extends "base.html" %}

{% block title %}Giáo viên · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell teacher-shell">
    <aside class="app-sidebar" aria-label="Điều hướng giáo viên">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Học sinh</span></a>
        {% for group, keys in [('Tổng quan', ['overview']), ('Nội dung', ['assignments', 'detective', 'argument', 'compare', 'debate']), ('Theo dõi', ['submissions', 'students', 'reports'])] %}
        <span class="ui-nav-group">{{ group }}</span>
        {% for key in keys %}{% set item = teacher_pages[key] %}
        <a class="sidebar-item {% if teacher_page == key %}active{% endif %}" {% if teacher_page == key %}aria-current="page"{% endif %} href="{{ url_for('main.teacher_page', page=key) }}"><i data-lucide="{{ item.icon }}"></i><span>{{ item.label }}</span></a>
        {% endfor %}{% endfor %}
        <a class="sidebar-item" href="{{ url_for('main.teacher_logout') }}"><i data-lucide="log-out"></i><span>Thoát</span></a>
    </aside>

    <section class="app-content teacher-page-content">
        <div class="teacher-top">
            <div><h1>{{ teacher_pages[teacher_page].label }}</h1></div>
            {% if teacher_page == "assignments" %}
            <a class="button primary" href="#newAssignment"><i data-lucide="plus"></i><span>Tạo nhiệm vụ</span></a>
            {% elif teacher_page == "compare" %}
            <a class="button primary" href="#newComparePackage"><i data-lucide="plus"></i><span>Tạo gói</span></a>
            {% elif teacher_page == "debate" %}
            <a class="button primary" href="#newDebateTopic"><i data-lucide="plus"></i><span>Tạo chủ đề</span></a>
            {% elif teacher_page == "detective" %}
            <a class="button primary" href="#newDetectiveCase"><i data-lucide="plus"></i><span>Tạo vụ án</span></a>
            {% elif teacher_page == "argument" %}
            <a class="button primary" href="#newArgumentPackage"><i data-lucide="plus"></i><span>Tạo gói</span></a>
            {% endif %}
        </div>

        {% if teacher_page == "overview" %}
        <div class="ui-metrics" aria-label="Thống kê lớp phụ trách">
            <article class="ui-metric"><strong>{{ learning.students|length }}</strong><span>Học sinh phụ trách</span></article>
            <article class="ui-metric"><strong>{{ assignment_submissions|rejectattr('teacher_score')|list|length }}</strong><span>Bài viết chờ giáo viên chấm</span></article>
            <article class="ui-metric"><strong>{{ assignment_tasks|selectattr('active')|list|length }}</strong><span>Nhiệm vụ đang mở</span></article>
        </div>
        {% include 'pages/teacher_learning_overview.html' %}
        {% endif %}

        {% if teacher_page == "debate" %}
        <section class="app-panel teacher-debate-panel">
            <div class="panel-heading"><div><h2>Chế độ ra chủ đề</h2></div></div>
            <form class="admin-form debate-mode-form" method="post" action="{{ url_for('main.teacher_debate_mode') }}">
                <div>
                    <label class="field-label" for="debateMode">Cách ra chủ đề</label>
                    <select id="debateMode" name="mode">
                        <option value="random" {% if debate_config.mode == "random" %}selected{% endif %}>Ngẫu nhiên</option>
                        <option value="priority" {% if debate_config.mode == "priority" %}selected{% endif %}>Ưu tiên lần lượt</option>
                        <option value="fixed" {% if debate_config.mode == "fixed" %}selected{% endif %}>Chủ đề cố định</option>
                    </select>
                </div>
                <div>
                    <label class="field-label" for="fixedTopic">Chủ đề cố định</label>
                    <select id="fixedTopic" name="fixed_topic_id">
                        {% for topic in debate_config.topics %}
                        <option value="{{ topic.id }}" {% if debate_config.fixed_topic_id == topic.id %}selected{% endif %}>{{ loop.index }}. {{ topic.title }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu</span></button>
            </form>
        </section>

        <section class="app-panel">
            <div class="panel-heading"><div><h2>Chủ đề và tiêu chí</h2></div></div>
            <div class="teacher-topic-list">
                {% for topic in debate_config.topics %}
                <article class="teacher-topic-card">
                    <details class="teacher-topic-editor">
                        <summary><span>Chủ đề {{ loop.index }}</span><strong>{{ topic.title }}</strong><em>{{ topic.side_a }} / {{ topic.side_b }}</em></summary>
                        <form class="admin-form" method="post" action="{{ url_for('main.teacher_debate_topic_save') }}">
                            <input type="hidden" name="topic_id" value="{{ topic.id }}">
                            <input name="title" value="{{ topic.title }}" required>
                            <div class="topic-side-grid">
                                <input name="side_a" value="{{ topic.side_a }}" required>
                                <input name="side_b" value="{{ topic.side_b }}" required>
                            </div>
                            <textarea name="criteria" rows="5">{{ criteria_to_text(topic.criteria) }}</textarea>
                            <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu chủ đề</span></button>
                        </form>
                        <form method="post" action="{{ url_for('main.teacher_debate_topic_delete', topic_id=topic.id) }}">
                            <button class="button secondary" type="submit"><i data-lucide="trash-2"></i><span>Xóa</span></button>
                        </form>
                    </details>
                </article>
                {% endfor %}
            </div>

            <details class="teacher-topic-add" id="newDebateTopic">
                <summary><i data-lucide="plus"></i><span>Thêm chủ đề</span></summary>
                <form class="admin-form teacher-topic-new" method="post" action="{{ url_for('main.teacher_debate_topic_save') }}">
                    <input name="title" placeholder="Chủ đề" required>
                    <div class="topic-side-grid">
                        <input name="side_a" placeholder="Phe A" required>
                        <input name="side_b" placeholder="Phe B" required>
                    </div>
                    <textarea name="criteria" rows="5" placeholder="Tiêu chí|điểm|từ khóa"></textarea>
                    <button class="button primary" type="submit"><i data-lucide="plus"></i><span>Lưu</span></button>
                </form>
            </details>
        </section>
        {% endif %}

        {% if teacher_page == "detective" %}
        <section class="app-panel">
            <div class="panel-heading"><div><h2>Dữ kiện Thám tử AI</h2></div></div>
            <details class="teacher-topic-add" id="newDetectiveCase">
                <summary><i data-lucide="plus"></i><span>Thêm vụ án</span></summary>
                <form class="admin-form teacher-topic-new" method="post" action="{{ url_for('main.teacher_detective_case_save') }}">
                    <div class="topic-side-grid">
                        <input name="code" placeholder="Mã trạm, ví dụ C" required>
                        <input name="title" placeholder="Tên lỗi" required>
                    </div>
                    <input name="field" placeholder="Lĩnh vực, ví dụ Kiểm chứng nguồn AI" required>
                    <input name="task" placeholder="Nhiệm vụ học sinh cần làm" required>
                    <textarea name="text" rows="4" placeholder="Câu trả lời AI có lỗi" required></textarea>
                    <div class="topic-side-grid">
                        <input name="error_type" placeholder="Loại lỗi" required>
                        <input name="suspicious_text" placeholder="Đoạn đáng nghi" required>
                    </div>
                    <textarea name="evidence" rows="3" placeholder="Bằng chứng/nguồn kiểm chứng" required></textarea>
                    <textarea name="rewrite" rows="3" placeholder="Gợi ý viết lại đúng hơn" required></textarea>
                    <label class="compare-active-check"><input type="checkbox" name="active" checked> Đang mở</label>
                    <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu vụ án</span></button>
                </form>
            </details>

            <div class="teacher-topic-list">
                {% for case in detective_cases %}
                <article class="teacher-topic-card">
                    <details class="teacher-topic-editor">
                        <summary><span>{{ case.code }}</span><strong>{{ case.title }}</strong><em>{{ case.field }} · {{ "Đang mở" if case.active else "Đã ẩn" }}</em></summary>
                        <form class="admin-form" method="post" action="{{ url_for('main.teacher_detective_case_save') }}">
                            <input type="hidden" name="case_id" value="{{ case.id }}">
                            <div class="topic-side-grid">
                                <input name="code" value="{{ case.code }}" required>
                                <input name="title" value="{{ case.title }}" required>
                            </div>
                            <input name="field" value="{{ case.field }}" required>
                            <input name="task" value="{{ case.task }}" required>
                            <textarea name="text" rows="4" required>{{ case.text }}</textarea>
                            <div class="topic-side-grid">
                                <input name="error_type" value="{{ case.error_type }}" required>
                                <input name="suspicious_text" value="{{ case.suspicious_text }}" required>
                            </div>
                            <textarea name="evidence" rows="3" required>{{ case.evidence }}</textarea>
                            <textarea name="rewrite" rows="3" required>{{ case.rewrite }}</textarea>
                            <label class="compare-active-check"><input type="checkbox" name="active" {% if case.active %}checked{% endif %}> Đang mở</label>
                            <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu</span></button>
                        </form>
                        <form method="post" action="{{ url_for('main.teacher_detective_case_delete', case_id=case.id) }}">
                            <button class="button secondary" type="submit"><i data-lucide="trash-2"></i><span>Xóa</span></button>
                        </form>
                    </details>
                </article>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "argument" %}
        <section class="app-panel">
            <div class="panel-heading"><div><h2>Gói câu hỏi Bản đồ lập luận</h2></div></div>
            <details class="teacher-topic-add" id="newArgumentPackage">
                <summary><i data-lucide="plus"></i><span>Thêm gói bản đồ</span></summary>
                <form class="admin-form teacher-topic-new" method="post" action="{{ url_for('main.teacher_argument_package_save') }}">
                    <input name="title" placeholder="Tên gói" required>
                    <textarea name="question" rows="2" placeholder="Câu hỏi trung tâm" required></textarea>
                    <textarea name="source_text" rows="4" placeholder="Đoạn văn nguồn" required></textarea>
                    <textarea name="pieces" rows="7" placeholder="Mỗi dòng: nội dung mảnh|claim/evidence/assumption/counter/conclusion" required></textarea>
                    <label class="compare-active-check"><input type="checkbox" name="active" checked> Đang mở</label>
                    <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu gói</span></button>
                </form>
            </details>

            <div class="review-list">
                <article><span>Nhóm phân loại</span><strong>{% for bucket in argument_buckets %}{{ bucket.key }} = {{ bucket.label }}{% if not loop.last %} · {% endif %}{% endfor %}</strong></article>
            </div>

            <div class="teacher-topic-list">
                {% for package in argument_packages %}
                <article class="teacher-topic-card">
                    <details class="teacher-topic-editor">
                        <summary><span>{{ "Đang mở" if package.active else "Đã ẩn" }}</span><strong>{{ package.title }}</strong><em>{{ package.teacher_name }}</em></summary>
                        <form class="admin-form" method="post" action="{{ url_for('main.teacher_argument_package_save') }}">
                            <input type="hidden" name="package_id" value="{{ package.id }}">
                            <input name="title" value="{{ package.title }}" required>
                            <textarea name="question" rows="2" required>{{ package.question }}</textarea>
                            <textarea name="source_text" rows="4" required>{{ package.source_text }}</textarea>
                            <textarea name="pieces" rows="7" required>{{ pieces_to_text(package.pieces) }}</textarea>
                            <label class="compare-active-check"><input type="checkbox" name="active" {% if package.active %}checked{% endif %}> Đang mở</label>
                            <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu</span></button>
                        </form>
                        <form method="post" action="{{ url_for('main.teacher_argument_package_delete', package_id=package.id) }}">
                            <button class="button secondary" type="submit"><i data-lucide="trash-2"></i><span>Xóa</span></button>
                        </form>
                    </details>
                </article>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "compare" %}
        <section class="app-panel teacher-compare-panel">
            <div class="panel-heading"><div><h2>Gói so sánh ba câu trả lời AI</h2></div></div>
            <details class="teacher-topic-add" id="newComparePackage">
                <summary><i data-lucide="plus"></i><span>Thêm gói bài</span></summary>
                <form class="admin-form teacher-topic-new compare-package-form" method="post" action="{{ url_for('main.teacher_compare_package_save') }}">
                    <input name="title" placeholder="Tên gói bài" required>
                    <textarea name="question" rows="3" placeholder="Câu hỏi học sinh cần đánh giá" required></textarea>
                    <textarea name="answer_a" rows="4" placeholder="Câu trả lời AI A" required></textarea>
                    <select name="trust_a" aria-label="Độ tin cậy câu A">
                        <option value="unclear">Mơ hồ</option>
                        <option value="source">Có nguồn</option>
                        <option value="no_source">Không nguồn</option>
                    </select>
                    <textarea name="answer_b" rows="4" placeholder="Câu trả lời AI B" required></textarea>
                    <select name="trust_b" aria-label="Độ tin cậy câu B">
                        <option value="unclear">Mơ hồ</option>
                        <option value="source">Có nguồn</option>
                        <option value="no_source">Không nguồn</option>
                    </select>
                    <textarea name="answer_c" rows="4" placeholder="Câu trả lời AI C" required></textarea>
                    <select name="trust_c" aria-label="Độ tin cậy câu C">
                        <option value="unclear">Mơ hồ</option>
                        <option value="source">Có nguồn</option>
                        <option value="no_source">Không nguồn</option>
                    </select>
                    <label>Giải thích đáp án đúng</label>
                    <textarea name="explanation" rows="4" required placeholder="Vì sao đáp án đúng? Các đáp án khác sai hoặc thiếu căn cứ ở đâu?"></textarea>
                    <div class="topic-side-grid">
                        <select name="best"><option value="A">A</option><option value="B">B</option><option value="C">C</option></select>
                        <label class="compare-active-check"><input type="checkbox" name="active" checked> Đang mở</label>
                    </div>
                    <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu gói</span></button>
                </form>
            </details>

            <div class="teacher-topic-list compare-teacher-list">
                {% for package in compare_packages %}
                <article class="teacher-topic-card">
                    <details class="teacher-topic-editor">
                        <summary><span>{{ "Đang mở" if package.active else "Đã ẩn" }}</span><strong>{{ package.title }}</strong><em>{{ package.teacher_name }}</em></summary>
                        <form class="admin-form compare-package-form" method="post" action="{{ url_for('main.teacher_compare_package_save') }}">
                            <input type="hidden" name="package_id" value="{{ package.id }}">
                            <input name="title" value="{{ package.title }}" required>
                            <textarea name="question" rows="3" required>{{ package.question }}</textarea>
                            <textarea name="answer_a" rows="4" required>{{ package.answers[0].text }}</textarea>
                            <select name="trust_a" aria-label="Độ tin cậy câu A">
                                <option value="unclear" {% if package.answers[0].trust == "unclear" %}selected{% endif %}>Mơ hồ</option>
                                <option value="source" {% if package.answers[0].trust == "source" %}selected{% endif %}>Có nguồn</option>
                                <option value="no_source" {% if package.answers[0].trust == "no_source" %}selected{% endif %}>Không nguồn</option>
                            </select>
                            <textarea name="answer_b" rows="4" required>{{ package.answers[1].text }}</textarea>
                            <select name="trust_b" aria-label="Độ tin cậy câu B">
                                <option value="unclear" {% if package.answers[1].trust == "unclear" %}selected{% endif %}>Mơ hồ</option>
                                <option value="source" {% if package.answers[1].trust == "source" %}selected{% endif %}>Có nguồn</option>
                                <option value="no_source" {% if package.answers[1].trust == "no_source" %}selected{% endif %}>Không nguồn</option>
                            </select>
                            <textarea name="answer_c" rows="4" required>{{ package.answers[2].text }}</textarea>
                            <select name="trust_c" aria-label="Độ tin cậy câu C">
                                <option value="unclear" {% if package.answers[2].trust == "unclear" %}selected{% endif %}>Mơ hồ</option>
                                <option value="source" {% if package.answers[2].trust == "source" %}selected{% endif %}>Có nguồn</option>
                                <option value="no_source" {% if package.answers[2].trust == "no_source" %}selected{% endif %}>Không nguồn</option>
                            </select>
                            <div class="topic-side-grid">
                                <label>Giải thích đáp án đúng<textarea name="explanation" rows="4" required>{{ package.get('explanation', '') }}</textarea></label>
                                <select name="best">
                                    <option value="A" {% if package.best == "A" %}selected{% endif %}>A</option>
                                    <option value="B" {% if package.best == "B" %}selected{% endif %}>B</option>
                                    <option value="C" {% if package.best == "C" %}selected{% endif %}>C</option>
                                </select>
                                <label class="compare-active-check"><input type="checkbox" name="active" {% if package.active %}checked{% endif %}> Đang mở</label>
                            </div>
                            <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu</span></button>
                        </form>
                        <form method="post" action="{{ url_for('main.teacher_compare_package_delete', package_id=package.id) }}">
                            <button class="button secondary" type="submit"><i data-lucide="trash-2"></i><span>Xóa</span></button>
                        </form>
                    </details>
                </article>
                {% endfor %}
            </div>
        </section>

        <section class="app-panel teacher-compare-panel">
            <div class="panel-heading"><div><h2>Bài học sinh đã nộp</h2></div></div>
            <div class="compare-submission-list">
                {% if compare_submissions %}
                    {% for submission in compare_submissions %}
                    <article>
                        <span>{{ submission.created_at[:10] }} · {{ submission.teacher_score or submission.score }}/100</span>
                        <strong>{{ submission.student_name }} · {{ submission.package_title }}</strong>
                        <p>Chọn câu {{ submission.selected }}. {{ submission.criteria|truncate(140) }}</p>
                        {% include 'pages/submission_feedback.html' %}
                        <form class="admin-form" method="post" action="{{ url_for('main.teacher_compare_submission_review', submission_id=submission.id) }}">
                            <input type="hidden" name="next" value="{{ url_for('main.teacher_page', page='compare') }}">
                            <input name="teacher_score" value="{{ submission.teacher_score }}" placeholder="Điểm cuối">
                            <textarea name="teacher_review" rows="3" placeholder="Nhận xét giáo viên">{{ submission.teacher_review }}</textarea>
                            <button class="button primary" type="submit"><i data-lucide="check"></i><span>Chốt đánh giá</span></button>
                        </form>
                    </article>
                    {% endfor %}
                {% else %}
                    <p class="muted-note">Chưa có bài nộp.</p>
                {% endif %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "assignments" %}
        <section class="app-panel teacher-assignment-panel">
            <div class="panel-heading"><div><h2>Nhiệm vụ cụ thể</h2></div></div>
            <details class="teacher-topic-add" id="newAssignment">
                <summary><i data-lucide="plus"></i><span>Thêm nhiệm vụ</span></summary>
                <form class="admin-form teacher-topic-new assignment-task-form" method="post" action="{{ url_for('main.teacher_assignment_task_save') }}">
                    <input name="title" placeholder="Tên nhiệm vụ" required>
                    <textarea name="prompt" rows="4" placeholder="Đề bài học sinh cần làm" required></textarea>
                    <textarea name="rubric" rows="5" placeholder="Rubric chấm điểm" required></textarea>
                    <label class="compare-active-check"><input type="checkbox" name="active" checked> Đang mở</label>
                    <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu nhiệm vụ</span></button>
                </form>
            </details>

            <div class="teacher-topic-list">
                {% for task in assignment_tasks %}
                <article class="teacher-topic-card">
                    <details class="teacher-topic-editor">
                        <summary><span>{{ "Đang mở" if task.active else "Đã ẩn" }}</span><strong>{{ task.title }}</strong><em>{{ task.teacher_name }}</em></summary>
                        <form class="admin-form assignment-task-form" method="post" action="{{ url_for('main.teacher_assignment_task_save') }}">
                            <input type="hidden" name="task_id" value="{{ task.id }}">
                            <input name="title" value="{{ task.title }}" required>
                            <textarea name="prompt" rows="4" required>{{ task.prompt }}</textarea>
                            <textarea name="rubric" rows="5" required>{{ task.rubric }}</textarea>
                            <label class="compare-active-check"><input type="checkbox" name="active" {% if task.active %}checked{% endif %}> Đang mở</label>
                            <button class="button primary" type="submit"><i data-lucide="save"></i><span>Lưu</span></button>
                        </form>
                        <form method="post" action="{{ url_for('main.teacher_assignment_task_delete', task_id=task.id) }}">
                            <button class="button secondary" type="submit"><i data-lucide="trash-2"></i><span>Xóa</span></button>
                        </form>
                    </details>
                </article>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "submissions" %}
        <section class="app-panel">
            <div class="panel-heading"><div><h2>Bài nộp cần chốt</h2></div></div>
            <div class="assignment-submission-list">
                {% if assignment_submissions %}
                    {% for submission in assignment_submissions %}
                    <article>
                        <details class="teacher-topic-editor">
                            <summary><span>{{ submission.teacher_score or "Chờ chấm" }}</span><strong>{{ submission.student_name }} · {{ submission.task_title }}</strong><em>{{ format_duration(submission.duration_seconds) }} · {{ submission.submitted_at[:10] }}</em></summary>
                            <div class="assignment-review-body">
                                {% if submission.get('synthetic') %}<p>Dữ liệu mô phỏng · Lượt {{ submission.get('attempt_number', 1) }} · Điểm mô phỏng: {{ submission.score }}/100. Chưa được giáo viên xác nhận.</p>{% endif %}
                                <h3>Bài làm</h3>
                                <p>{{ submission.answer }}</p>
                                <h3>AI nhận xét sơ bộ</h3>
                                <p>{{ submission.ai_review }}</p>
                                <h3>Trao đổi với AI</h3>
                                <div class="assignment-chat-log">
                                    {% for message in submission.chat %}
                                    <p><strong>{{ "HS" if message.role == "student" else "AI" }}:</strong> {{ message.content }}</p>
                                    {% endfor %}
                                </div>
                                <form class="admin-form" method="post" action="{{ url_for('main.teacher_assignment_submission_review', submission_id=submission.id) }}">
                                    <input name="teacher_score" value="{{ submission.teacher_score }}" placeholder="Điểm cuối">
                                    <textarea name="teacher_review" rows="4" placeholder="Nhận xét giáo viên">{{ submission.teacher_review }}</textarea>
                                    <button class="button primary" type="submit"><i data-lucide="check"></i><span>Chốt đánh giá</span></button>
                                </form>
                            </div>
                        </details>
                    </article>
                    {% endfor %}
                {% else %}
                    <p class="muted-note">Chưa có bài nộp.</p>
                {% endif %}
            </div>
        </section>

        <section class="app-panel">
            <div class="panel-heading"><div><h2>Bài so sánh AI</h2></div></div>
            <div class="assignment-submission-list">
                {% if compare_submissions %}
                    {% for submission in compare_submissions %}
                    <article>
                        <details class="teacher-topic-editor">
                            <summary><span>{{ submission.teacher_score or submission.score }}</span><strong>{{ submission.student_name }} · {{ submission.package_title }}</strong><em>{{ submission.created_at[:10] }}</em></summary>
                            <div class="assignment-review-body">
                                <h3>Câu hỏi</h3>
                                <p>{{ submission.question }}</p>
                                <h3>Bài làm học sinh</h3>
                                <p>Chọn câu {{ submission.selected }}. {{ "Đúng đáp án gợi ý" if submission.correct else "Khác đáp án gợi ý" }}.</p>
                                <p>{{ submission.criteria }}</p>
                                <h3>Câu trả lời học sinh viết lại</h3>
                                <p>{{ submission.synthesis }}</p>
                                {% include 'pages/submission_feedback.html' %}
                                <form class="admin-form" method="post" action="{{ url_for('main.teacher_compare_submission_review', submission_id=submission.id) }}">
                                    <input name="teacher_score" value="{{ submission.teacher_score }}" placeholder="Điểm cuối">
                                    <textarea name="teacher_review" rows="4" placeholder="Nhận xét giáo viên">{{ submission.teacher_review }}</textarea>
                                    <button class="button primary" type="submit"><i data-lucide="check"></i><span>Chốt đánh giá</span></button>
                                </form>
                            </div>
                        </details>
                    </article>
                    {% endfor %}
                {% else %}
                    <p class="muted-note">Chưa có bài so sánh AI.</p>
                {% endif %}
            </div>
        </section>

        <section class="app-panel">
            <div class="panel-heading"><div><h2>Bài mô-đun giáo viên ra đề</h2></div></div>
            <div class="assignment-submission-list">
                {% if teacher_content_submissions %}
                    {% for submission in teacher_content_submissions %}
                    <article>
                        <details class="teacher-topic-editor">
                            <summary><span>{{ submission.teacher_score or submission.score }}</span><strong>{{ submission.student_name }} · {{ submission.module_title }}</strong><em>{{ submission.submitted_at[:10] }}</em></summary>
                            <div class="assignment-review-body">
                                {% if submission.kind == "argument" %}
                                {% include 'pages/submission_feedback.html' %}
                                <h3>{{ submission.package_title }}</h3>
                                <p>{{ submission.question }}</p>
                                <h3>Kết quả phân loại</h3>
                                <p>{{ submission.correct }}/{{ submission.total }} mảnh đúng. AI chấm sơ bộ {{ submission.ai_score }}/100.</p>
                                <div class="assignment-chat-log">
                                    {% for placement in submission.placements %}
                                    <p><strong>{{ placement.bucket_label }}:</strong> {{ placement.piece_text }}</p>
                                    {% endfor %}
                                </div>
                                {% else %}
                                <h3>{{ submission.case_code }} · {{ submission.case_title }}</h3>
                                {% include 'pages/submission_feedback.html' %}
                                <p>{{ submission.task }}</p>
                                <h3>Bài làm học sinh</h3>
                                <p><strong>Đoạn đáng nghi:</strong> {{ submission.suspicious_text }}</p>
                                <p><strong>Loại lỗi:</strong> {{ submission.error_type }}</p>
                                <p><strong>Giải thích:</strong> {{ submission.explanation }}</p>
                                <p><strong>Bằng chứng:</strong> {{ submission.evidence }}</p>
                                <p><strong>Viết lại:</strong> {{ submission.rewrite }}</p>
                                {% endif %}
                                <form class="admin-form" method="post" action="{{ url_for('main.teacher_content_submission_review', submission_id=submission.id) }}">
                                    <input name="teacher_score" value="{{ submission.teacher_score }}" placeholder="Điểm cuối">
                                    <textarea name="teacher_review" rows="4" placeholder="Nhận xét giáo viên">{{ submission.teacher_review }}</textarea>
                                    <button class="button primary" type="submit"><i data-lucide="check"></i><span>Chốt đánh giá</span></button>
                                </form>
                            </div>
                        </details>
                    </article>
                    {% endfor %}
                {% else %}
                    <p class="muted-note">Chưa có bài nộp từ Bản đồ lập luận hoặc Thám tử AI.</p>
                {% endif %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "students" %}
        <section class="app-panel">
            <div class="panel-heading"><div><h2>Theo dõi học sinh</h2></div></div>
            <div class="student-table">
                <div class="student-table-head"><span>Học sinh</span><span>Trường</span><span>Lớp</span></div>
                {% for student in learning.students %}
                <article><strong>{{ student.name }}</strong><span>{{ student.school }}</span><span>{{ student.class_name }}</span></article>
                {% else %}<div class="ui-empty">Chưa có học sinh trong lớp phụ trách.</div>{% endfor %}
            </div>
        </section>
        {% endif %}

        {% if teacher_page == "reports" %}
        <div class="teacher-grid">
            <section class="app-panel">
                <div class="panel-heading"><div><h2>Bài so sánh gần nhất</h2></div></div>
                <div class="compare-submission-list">
                    {% if compare_submissions %}
                        {% for submission in compare_submissions %}
                        <article><span>{{ submission.created_at[:10] }} · {{ submission.score }}/100</span><strong>{{ submission.student_name }} · {{ submission.package_title }}</strong><p>Chọn câu {{ submission.selected }}. {{ submission.criteria|truncate(130) }}</p></article>
                        {% endfor %}
                    {% else %}
                        <p class="muted-note">Chưa có bài nộp.</p>
                    {% endif %}
                </div>
            </section>

            <section class="app-panel teacher-report-inbox">
                <div class="panel-heading"><div><h2>Hộp thư giáo viên</h2></div></div>
                <div class="report-list">
                    {% if reports %}
                        {% for report in reports %}
                        <article><span>{{ report.created_at[:10] }}</span><strong>{{ report.title }}</strong><p>{{ report.body }}</p></article>
                        {% endfor %}
                    {% else %}
                        <p class="muted-note">Chưa có báo cáo.</p>
                    {% endif %}
                </div>
            </section>
        </div>
        {% endif %}
    </section>
</div>
{% endblock %}

```

## app/templates/pages/trust_calibration.html

```html
{% extends "base.html" %}

{% block title %}Tin hay không tin? · AI Critical Thinking Lab{% endblock %}

{% block content %}
<div class="app-shell module-shell">
    <aside class="app-sidebar" aria-label="Danh sách mô-đun">
        <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
        {% for nav_item in modules %}
        <a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}">
            <i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span>
        </a>
        {% endfor %}
    </aside>

    <section class="app-content">
        <div class="module-detail-hero">
            <div>
                <p class="eyebrow dark">{{ module.area }}</p>
                <h1>{{ module.title }}</h1>
            </div>
            <button class="button primary" type="button" id="nextTrustItem"><i data-lucide="shuffle"></i><span>Câu tiếp</span></button>
        </div>

        <section class="trust-layout" data-total="{{ item_count }}">
            <article class="app-panel trust-card" id="trustCard" data-item-id="{{ item.id }}" data-index="0">
                <p class="eyebrow dark">Câu hỏi</p>
                <h2 id="trustQuestion">{{ item.question }}</h2>
                <div class="ai-answer-box" id="trustAiAnswer">{{ item.ai_answer }}</div>
            </article>

            <aside class="app-panel trust-control">
                <div class="trust-slider-block">
                    <label for="trustInitial">Mức tin cậy ban đầu</label>
                    <strong><span id="trustInitialValue">50</span>%</strong>
                    <input id="trustInitial" type="range" min="0" max="100" value="50">
                    <button class="button primary" type="button" id="lockTrustInitial"><i data-lucide="lock"></i><span>Chốt mức tin cậy</span></button>
                </div>
                <div class="evidence-box" id="trustEvidence" hidden></div>
                <div class="trust-slider-block" id="trustRevisedBlock" hidden>
                    <label for="trustRevised">Mức tin cậy sau bằng chứng</label>
                    <strong><span id="trustRevisedValue">50</span>%</strong>
                    <input id="trustRevised" type="range" min="0" max="100" value="50">
                    <button class="button primary" type="button" id="scoreTrust"><i data-lucide="check"></i><span>Xem kết quả</span></button>
                </div>
            </aside>
        </section>

        <section class="app-panel trust-result" id="trustResult" hidden>
            <div class="calibration-bar">
                <span class="marker initial" id="markerInitial">Ban đầu</span>
                <span class="marker revised" id="markerRevised">Sau</span>
                <span class="marker truth" id="markerTruth">Đúng</span>
            </div>
            <p id="trustExplanation"></p>
        </section>
    </section>
</div>
{% endblock %}

```

## app/templates/pages/workshop_sidebar.html

```html
<aside class="app-sidebar" aria-label="Danh sách mô-đun">
    <a class="sidebar-item" href="{{ url_for('main.app_home') }}"><i data-lucide="arrow-left"></i><span>Quay lại</span></a>
    {% for nav_item in modules %}<a class="sidebar-item {% if nav_item.slug == module.slug %}active{% endif %}" href="{{ url_for('main.module_detail', slug=nav_item.slug) }}"><i data-lucide="{{ nav_item.icon }}"></i><span>{{ nav_item.title }}</span></a>{% endfor %}
</aside>

```

## app/static/css/design-tokens.css

```css
/* Shared notebook system. Loaded only outside the preserved home pages. */
body {
    --ui-bg: #FAF8F3;
    --ui-surface: #FFFFFF;
    --ui-border: #E8E4DA;
    --ui-primary: #2563EB;
    --ui-primary-hover: #1D4ED8;
    --ui-primary-soft: #EFF6FF;
    --ui-link: #1D4ED8;
    --ui-ai: #7C3AED;
    --ui-ai-soft: #F5F3FF;
    --ui-success: #16A34A;
    --ui-success-text: #166534;
    --ui-success-soft: #F0FDF4;
    --ui-warning: #D97706;
    --ui-warning-text: #92400E;
    --ui-warning-soft: #FFFBEB;
    --ui-danger: #DC2626;
    --ui-danger-soft: #FEF2F2;
    --ui-text: #1F2937;
    --ui-secondary: #4B5563;
    --ui-muted: #6B7280;
    --ui-dark-bg: #0F172A;
    --ui-dark-surface: #1E293B;
    --ui-dark-border: #334155;
    --ui-dark-text: #F1F5F9;
    --ui-dark-secondary: #CBD5E1;
    --ui-ring: rgb(37 99 235 / 25%);
    --ui-overlay: rgb(15 23 42 / 55%);
    --ui-shadow: 0 1px 2px rgb(0 0 0 / 4%), 0 4px 16px rgb(0 0 0 / 4%);
    --ui-shadow-raised: 0 12px 32px rgb(15 23 42 / 10%);
    --ui-font: 'Be Vietnam Pro', system-ui, sans-serif;
    --ui-space-1: 4px;
    --ui-space-2: 8px;
    --ui-space-3: 12px;
    --ui-space-4: 16px;
    --ui-space-5: 24px;
    --ui-space-6: 32px;
    --ui-space-7: 48px;
    --ui-space-8: 64px;
    --ui-radius-control: 10px;
    --ui-radius-card: 16px;
    --ui-radius-modal: 20px;
    --ui-radius-pill: 999px;
    --ui-transition: 180ms ease;
    /* Existing components inherit these aliases without changing JS/state. */
    --bg-page: var(--ui-bg);
    --bg-card: var(--ui-surface);
    --paper: var(--ui-bg);
    --white: var(--ui-surface);
    --panel: var(--ui-surface);
    --panel-soft: var(--ui-primary-soft);
    --surface: var(--ui-surface);
    --text: var(--ui-text);
    --text-primary: var(--ui-text);
    --text-secondary: var(--ui-secondary);
    --ink: var(--ui-text);
    --muted: var(--ui-muted);
    --soft: var(--ui-bg);
    --line: var(--ui-border);
    --accent-primary: var(--ui-primary);
    --accent-secondary: var(--ui-ai);
    --indigo: var(--ui-primary);
    --indigo-dark: var(--ui-primary-hover);
    --coral: var(--ui-primary);
    --success: var(--ui-success);
    --warning: var(--ui-warning);
    --danger: var(--ui-danger);
}
body.game-page {
    --ui-link: #93C5FD;
    --ui-bg: var(--ui-dark-bg);
    --ui-surface: var(--ui-dark-surface);
    --ui-border: var(--ui-dark-border);
    --ui-text: var(--ui-dark-text);
    --ui-secondary: var(--ui-dark-secondary);
    --ui-muted: var(--ui-dark-secondary);
    --ui-primary-soft: var(--ui-dark-border);
    --ui-ai-soft: var(--ui-dark-border);
}

```

## app/static/css/design-system.css

```css
/* Important declarations in this named layer supersede legacy overrides.
   The file is excluded entirely from / and /app to preserve their rendering. */
@layer notebook {
    body { background: var(--ui-bg) !important; color: var(--ui-text) !important; font-family: var(--ui-font) !important; font-size: 16px !important; line-height: 1.6 !important; }
    body *, body *::before, body *::after { box-sizing: border-box !important; }
    body *:not(.ti) { font-family: var(--ui-font) !important; }
    body :is(h1,h2,h3,h4,input,select,textarea,button,.button) { font-family: var(--ui-font) !important; }
    body h1 { font-size: 1.75rem !important; font-weight: 700 !important; line-height: 1.25 !important; letter-spacing: -.035em !important; color: var(--ui-text) !important; margin: 0 0 12px !important; }
    body h2 { font-size: 1.375rem !important; font-weight: 600 !important; line-height: 1.25 !important; color: var(--ui-text) !important; }
    body h3 { font-size: 1.125rem !important; line-height: 1.4 !important; color: var(--ui-text) !important; }
    body :is(p,li,.assignment-full-prompt,.argument-piece,.compare-card p,#detectiveText,.assignment-review-body) { font-size: 1rem !important; line-height: 1.7 !important; color: var(--ui-secondary) !important; overflow-wrap: anywhere !important; }
    body :is(small,.response-meta,.muted-note,.eyebrow,.workshop-kicker,.task-subject,.draft-status,.hero-skills,.hero-stamp) { font-size: .875rem !important; color: var(--ui-muted) !important; letter-spacing: normal !important; }
    body :is(.field-label,label) { color: var(--ui-text) !important; font-size: .9375rem !important; font-weight: 500 !important; }
    body .field-label { display: block !important; margin: 16px 0 8px !important; }
    body :is(strong,.panel-heading,.student-table-head) { color: var(--ui-text) !important; }
    body :is(a,button,input,select,textarea,summary,[tabindex]):focus-visible { outline: 3px solid var(--ui-ring) !important; outline-offset: 3px !important; }
    body :is(button,.button,.header-cta,.password-toggle,.filter-tab,.task-filters button) { min-height: 44px !important; min-width: 44px !important; border-radius: var(--ui-radius-control) !important; cursor: pointer !important; transition: background var(--ui-transition), transform var(--ui-transition), box-shadow var(--ui-transition) !important; font-size: .9375rem !important; }
    body .button { display: inline-flex !important; align-items: center !important; justify-content: center !important; gap: 8px !important; padding: 10px 20px !important; font-weight: 600 !important; box-shadow: none !important; }
    body .button.ui-secondary-action { background: var(--ui-surface) !important; border: 1px solid var(--ui-primary) !important; color: var(--ui-primary) !important; }
    body svg.lucide { width: 20px !important; height: 20px !important; flex-shrink: 0 !important; stroke-width: 1.75 !important; }
    body :where(.button.primary,.header-cta,#scoreArgumentMap,.assignment-chat-form button) { background: var(--ui-primary) !important; border: 1px solid var(--ui-primary) !important; color: var(--ui-dark-text) !important; }
    body :is(.button.primary,.header-cta):hover { background: var(--ui-primary-hover) !important; }
    body :is(.button.secondary,.filter-tab,.task-filters button) { background: var(--ui-surface) !important; color: var(--ui-primary) !important; border: 1px solid var(--ui-border) !important; }
    body :is(.button.secondary,.filter-tab):hover { background: var(--ui-primary-soft) !important; }
    body .button.ui-secondary-action:hover { background: var(--ui-primary-soft) !important; color: var(--ui-primary) !important; }
    body :is(.button.danger,button[data-ui-danger]) { background: var(--ui-danger-soft) !important; color: var(--ui-danger) !important; border: 1px solid var(--ui-danger) !important; }
    body :is(button:disabled,.button[aria-disabled=true]) { opacity: .55 !important; cursor: not-allowed !important; transform: none !important; }
    body :is(input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=hidden]),select,textarea) { background: var(--ui-surface) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-control) !important; min-height: 44px !important; padding: 11px 14px !important; font-size: 1rem !important; line-height: 1.6 !important; min-width: 0 !important; max-width: 100% !important; box-shadow: none !important; }
    body textarea { width: 100% !important; min-height: 140px !important; resize: vertical !important; }
    body :is(input,textarea)::placeholder { color: var(--ui-muted) !important; }
    body :is(input,select,textarea):focus { border-color: var(--ui-primary) !important; outline: 3px solid var(--ui-ring) !important; }
    body :is(.app-panel,.workshop-card,.auth-card,.compare-card,.detective-task,.detective-form,.piece-tray,.argument-canvas,.thinking-board,.socratic-chat-panel,.teacher-topic-card,.learning-feedback) { background: var(--ui-surface) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; box-shadow: var(--ui-shadow) !important; padding: 24px !important; min-width: 0 !important; }
    body :is(.app-panel,.workshop-card) { margin-bottom: 24px !important; }
    body :is(.module-detail-hero,.teacher-top,.workshop-hero) { display: flex !important; align-items: center !important; justify-content: space-between !important; flex-wrap: wrap !important; gap: 24px !important; background: transparent !important; border: 0 !important; border-bottom: 1px solid var(--ui-border) !important; border-radius: 0 !important; padding: 16px 0 32px !important; margin-bottom: 32px !important; box-shadow: none !important; }
    body .workshop-hero h1 { font-size: 2rem !important; }
    body :is(.hero-symbol,.section-icon,.assignment-task-icon) { background: var(--ui-primary-soft) !important; color: var(--ui-primary) !important; border-radius: var(--ui-radius-card) !important; transform: none !important; box-shadow: none !important; }
    body .hero-symbol { width: 72px !important; height: 72px !important; }
    body :is(.prompt-hero .hero-symbol,.purple,.assignment-chat-toggle) { color: var(--ui-ai) !important; background: var(--ui-ai-soft) !important; }
    body .site-header { display: flex !important; position: sticky !important; top: 0 !important; z-index: 70 !important; height: 76px !important; padding: 12px 32px !important; background: var(--ui-surface) !important; border-bottom: 1px solid var(--ui-border) !important; box-shadow: none !important; gap: 20px !important; }
    body .brand { font: 700 1.125rem/1.3 var(--ui-font) !important; color: var(--ui-text) !important; }
    body .brand-mark { background: var(--ui-primary) !important; color: var(--ui-dark-text) !important; box-shadow: none !important; }
    body .main-nav { margin-left: auto !important; font-size: .875rem !important; }
    body .site-footer { color: var(--ui-muted) !important; padding: 24px 32px !important; background: var(--ui-bg) !important; border-top: 1px solid var(--ui-border) !important; }
    body main::before,body main::after { display: none !important; }
    body .module-focus-back { display: none !important; }
    body .app-shell { display: grid !important; grid-template-columns: 240px minmax(0,1fr) !important; gap: 32px !important; width: 100% !important; max-width: 1600px !important; margin: 0 auto !important; padding: 32px !important; background: transparent !important; }
    body .app-shell.module-shell { display: block !important; max-width: 1360px !important; }
    body .app-shell.module-shell > .app-sidebar { display: none !important; }
    body .app-content { width: 100% !important; max-width: none !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important; background: transparent !important; border: 0 !important; box-shadow: none !important; }
    body .app-content { font-size: 1rem !important; line-height: 1.6 !important; }
    body .app-shell.module-shell > .app-sidebar.ui-drawer-open { display: flex !important; position: fixed !important; top: 84px !important; left: 16px !important; bottom: 16px !important; z-index: 80 !important; box-shadow: var(--ui-shadow-raised) !important; }
    body .app-sidebar { display: flex !important; flex-direction: column !important; gap: 6px !important; width: 240px !important; background: var(--ui-surface) !important; padding: 16px !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; position: sticky !important; top: 100px !important; height: fit-content !important; max-height: calc(100dvh - 124px) !important; overflow-y: auto !important; }
    body .sidebar-item { display: flex !important; align-items: center !important; gap: 12px !important; padding: 12px !important; min-height: 48px !important; color: var(--ui-secondary) !important; border-radius: var(--ui-radius-control) !important; font-size: .875rem !important; }
    body .sidebar-item.active { color: var(--ui-primary) !important; background: var(--ui-primary-soft) !important; border-left: 3px solid var(--ui-primary) !important; }
    body .ui-nav-group { font-size: .8125rem !important; font-weight: 600 !important; color: var(--ui-muted) !important; padding: 20px 12px 4px !important; }
    body .ui-breadcrumb { display: flex !important; gap: 8px !important; align-items: center !important; flex-wrap: wrap !important; color: var(--ui-muted) !important; font-size: .875rem !important; margin-bottom: 24px !important; }
    body .ui-back { color: var(--ui-primary) !important; min-height: 44px !important; display: inline-flex !important; align-items: center !important; gap: 8px !important; }
    body .workshop-breadcrumb { display: none !important; }
    body .ui-menu-toggle { background: var(--ui-primary-soft) !important; color: var(--ui-primary) !important; border: 1px solid var(--ui-border) !important; padding: 8px 12px !important; }
    body .ui-toolbar { display: flex !important; gap: 12px !important; flex-wrap: wrap !important; align-items: center !important; margin-bottom: 24px !important; padding: 16px !important; background: var(--ui-surface) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body .ui-toolbar input { flex: 1 1 240px !important; width: auto !important; }
    body .ui-toolbar label { display: flex !important; gap: 8px !important; align-items: center !important; }
    body .ui-result-count { color: var(--ui-muted) !important; font-size: .875rem !important; }
    body .assignment-task-grid { display: grid !important; grid-template-columns: repeat(3,minmax(0,1fr)) !important; gap: 24px !important; }
    body .assignment-task-box { display: flex !important; flex-direction: column !important; gap: 12px !important; padding: 24px !important; min-height: 220px !important; background: var(--ui-surface) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; box-shadow: var(--ui-shadow) !important; color: var(--ui-text) !important; transition: transform var(--ui-transition),box-shadow var(--ui-transition) !important; }
    body .assignment-task-box:hover { transform: translateY(-3px) !important; box-shadow: var(--ui-shadow-raised) !important; border-color: var(--ui-primary) !important; }
    body .assignment-task-box :is(strong,h3) { font-size: 1.125rem !important; line-height: 1.45 !important; }
    body .assignment-task-box em { color: var(--ui-muted) !important; font-size: .875rem !important; font-style: normal !important; }
    body .compare-package-list { display: grid !important; grid-template-columns: repeat(3,minmax(0,1fr)) !important; gap: 24px !important; }
    body .compare-package-card { padding: 24px !important; min-height: 180px !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; background: var(--ui-surface) !important; display: flex !important; flex-direction: column !important; gap: 12px !important; box-shadow: var(--ui-shadow) !important; }
    body .compare-package-card strong { font-size: 1.125rem !important; }
    body .compare-package-card span { color: var(--ui-secondary) !important; font-size: .875rem !important; }
    body .compare-package-card em { font-style: normal !important; color: var(--ui-primary) !important; margin-top: auto !important; }
    body .task-search { position: relative !important; }
    body .task-search > svg { display: none !important; }
    body .task-number,body .task-card-bottom,body .task-card-bottom span { color: var(--ui-muted) !important; font-size: .8125rem !important; }
    body .assignment-task-action { color: var(--ui-primary) !important; margin-top: auto !important; font-size: .875rem !important; }
    body .ui-badge { display: inline-flex !important; align-items: center !important; gap: 6px !important; border-radius: var(--ui-radius-pill) !important; padding: 4px 10px !important; font-size: .8125rem !important; font-weight: 600 !important; width: fit-content !important; color: var(--ui-primary) !important; background: var(--ui-primary-soft) !important; }
    body :is(.ui-empty,.assignment-empty,.task-search-empty) { text-align: center !important; padding: 40px 24px !important; color: var(--ui-muted) !important; border: 1px dashed var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body .auth-page { min-height: calc(100dvh - 154px) !important; display: grid !important; place-items: center !important; padding: 48px 20px !important; background: var(--ui-bg) !important; }
    body .auth-card { width: 100% !important; max-width: 460px !important; padding: 32px !important; display: flex !important; flex-direction: column !important; gap: 4px !important; }
    body .auth-card h1 { margin-top: 12px !important; }
    body .auth-card > .button { margin-top: 24px !important; }
    body .auth-links { display: flex !important; justify-content: space-between !important; gap: 16px !important; flex-wrap: wrap !important; margin-top: 20px !important; font-size: .875rem !important; }
    body .text-link { color: var(--ui-primary) !important; }
    body .password-field { width: 100% !important; display: flex !important; position: relative !important; }
    body .password-field input { width: 100% !important; padding-right: 52px !important; }
    body .password-toggle { position: absolute !important; right: 1px !important; top: 1px !important; background: transparent !important; border: 0 !important; color: var(--ui-secondary) !important; }
    body .ui-role-tabs { display: grid !important; grid-template-columns: repeat(3,1fr) !important; gap: 4px !important; background: var(--ui-bg) !important; border: 1px solid var(--ui-border) !important; padding: 4px !important; border-radius: var(--ui-radius-control) !important; }
    body .ui-role-tabs button { background: transparent !important; border: 0 !important; color: var(--ui-secondary) !important; padding: 8px !important; font-size: .875rem !important; }
    body .ui-role-tabs button[aria-pressed=true] { background: var(--ui-surface) !important; box-shadow: var(--ui-shadow) !important; color: var(--ui-primary) !important; }
    body .ui-fieldset { margin: 16px 0 0 !important; border: 0 !important; padding: 0 !important; min-width: 0 !important; }
    body .ui-fieldset legend { font-size: 1rem !important; font-weight: 600 !important; padding: 0 !important; color: var(--ui-text) !important; }
    body .ui-help { font-size: .8125rem !important; color: var(--ui-muted) !important; margin-top: 6px !important; }
    body :is(.auth-error,[role=alert]) { color: var(--ui-danger) !important; background: var(--ui-danger-soft) !important; border: 1px solid var(--ui-danger) !important; padding: 12px 16px !important; border-radius: var(--ui-radius-control) !important; }
    body :is(.auth-success,.green) { color: var(--ui-success-text) !important; background: var(--ui-success-soft) !important; }
    body :is(.assignment-full-prompt,.argument-source-text,#detectiveText,.assignment-review-body > p,.compare-card p) { max-width: 68ch !important; white-space: pre-line !important; }
    body :is(.assignment-task-card,.argument-source,.detective-task) { background: var(--ui-primary-soft) !important; }
    body :is(.assignment-workspace,.prompt-workspace,.detective-layout,.argument-workspace,.socratic-workspace,.gemini-grid,.profile-grid,.teacher-grid) { display: grid !important; grid-template-columns: minmax(0,1.3fr) minmax(0,1fr) !important; gap: 24px !important; align-items: start !important; }
    body .assignment-form { grid-column: 1 / -1 !important; }
    body :is(.assignment-writing-grid,.compare-grid) { gap: 24px !important; }
    body :is(.assignment-submit-bar,.ui-form-actions) { position: sticky !important; bottom: 12px !important; z-index: 15 !important; background: var(--ui-surface) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; padding: 16px !important; box-shadow: var(--ui-shadow) !important; display: flex !important; justify-content: space-between !important; gap: 12px !important; flex-wrap: wrap !important; }
    body :is(.assignment-timer,.trust-badge) { color: var(--ui-primary) !important; background: var(--ui-primary-soft) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; padding: 12px 16px !important; }
    body .assignment-timer strong { font-size: 1.75rem !important; font-variant-numeric: tabular-nums !important; }
    body :is(.chat-thread,.assignment-chat-thread) { background: var(--ui-bg) !important; padding: 16px !important; min-height: 300px !important; max-height: 60dvh !important; overflow-y: auto !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body .socratic-message { max-width: 88% !important; border: 0 !important; border-radius: var(--ui-radius-card) !important; padding: 16px !important; margin: 12px 0 !important; }
    body .socratic-message.ai { background: var(--ui-ai-soft) !important; color: var(--ui-text) !important; margin-right: auto !important; }
    body .socratic-message.user { background: var(--ui-primary) !important; color: var(--ui-dark-text) !important; margin-left: auto !important; }
    body .socratic-message.user :is(p,span,strong) { color: var(--ui-dark-text) !important; }
    body .socratic-message.ai > span { color: var(--ui-ai) !important; }
    body .socratic-form { position: sticky !important; bottom: 12px !important; background: var(--ui-surface) !important; padding-top: 16px !important; }
    body .socratic-form textarea { min-height: 88px !important; }
    body :is(.stage-pill,.socratic-mode-button,.board-section,.detective-hint) { background: var(--ui-bg) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-control) !important; }
    body :is(.stage-pill.active,.socratic-mode-button.active,.filter-tab.active,.task-filters button.active) { background: var(--ui-primary-soft) !important; color: var(--ui-primary) !important; border-color: var(--ui-primary) !important; }
    body .stage-pill :is(span,small) { color: inherit !important; font-size: .8125rem !important; }
    body .socratic-stagebar { gap: 8px !important; margin-bottom: 24px !important; }
    body .argument-bucket { border-radius: var(--ui-radius-card) !important; padding: 16px !important; min-height: 130px !important; border: 1px solid var(--ui-border) !important; }
    body .argument-bucket[data-bucket-key=claim] { background: var(--ui-primary-soft) !important; border-color: var(--ui-primary) !important; }
    body .argument-bucket[data-bucket-key=evidence],body .argument-bucket[data-bucket-key=conclusion] { background: var(--ui-success-soft) !important; border-color: var(--ui-success) !important; }
    body .argument-bucket[data-bucket-key=assumption] { background: var(--ui-ai-soft) !important; border-color: var(--ui-ai) !important; }
    body .argument-bucket[data-bucket-key=counter] { background: var(--ui-warning-soft) !important; border-color: var(--ui-warning) !important; }
    body .argument-piece { background: var(--ui-surface) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-control) !important; padding: 12px !important; color: var(--ui-text) !important; cursor: grab !important; }
    body .radar-chart { width: 100% !important; max-width: 460px !important; min-height: 360px !important; margin: auto !important; }
    body .radar-chart svg { width: 100% !important; height: auto !important; }
    body .progress-track { background: var(--ui-border) !important; height: 8px !important; border-radius: var(--ui-radius-pill) !important; }
    body .progress-track > span { background: var(--ui-primary) !important; border-radius: inherit !important; }
    body .assignment-consent { background: var(--ui-overlay) !important; backdrop-filter: blur(4px) !important; z-index: 120 !important; padding: 24px !important; }
    body .assignment-consent-card { background: var(--ui-surface) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-modal) !important; max-width: 560px !important; width: 100% !important; padding: 32px !important; box-shadow: var(--ui-shadow-raised) !important; }
    body .assignment-consent-card > div { display: flex !important; flex-direction: row-reverse !important; gap: 12px !important; }
    body .student-table { overflow-x: auto !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body :is(.student-table-head,.student-table > article) { padding: 16px !important; gap: 16px !important; min-width: 580px !important; border-bottom: 1px solid var(--ui-border) !important; }
    body .student-table-head { position: sticky !important; top: 0 !important; background: var(--ui-bg) !important; font-weight: 600 !important; }
    body :is(.student-table > article,.assignment-submission-list > article):hover { background: var(--ui-primary-soft) !important; }
    body .teacher-topic-editor > summary { padding: 16px !important; min-height: 60px !important; gap: 16px !important; cursor: pointer !important; border-bottom: 1px solid var(--ui-border) !important; }
    body .teacher-topic-editor[open] { background: var(--ui-surface) !important; border: 1px solid var(--ui-primary) !important; border-radius: var(--ui-radius-card) !important; padding: 8px !important; }
    body .assignment-review-body { padding: 24px !important; }
    body .assignment-review-body form { border-top: 1px solid var(--ui-border) !important; margin-top: 24px !important; padding-top: 24px !important; }
    body .ui-review-grid { display: grid !important; grid-template-columns: minmax(0,1.5fr) minmax(260px,1fr) !important; gap: 32px !important; }
    body .ui-review-grid form { margin-top: 0 !important; padding-top: 0 !important; border-top: 0 !important; }
    body .ui-review-answer { min-width: 0 !important; }
    body .ui-preview { padding: 24px !important; margin: 24px 0 !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; background: var(--ui-primary-soft) !important; }
    body .ui-preview summary { cursor: pointer !important; color: var(--ui-primary) !important; min-height: 44px !important; font-weight: 600 !important; }
    body .ui-preview p { white-space: pre-wrap !important; max-width: 68ch !important; }
    body :is(.trust-layout,.human-first-grid,.error-layout) { display: grid !important; grid-template-columns: minmax(0,1fr) minmax(0,1fr) !important; gap: 24px !important; }
    body :is(.ai-answer-box,.evidence-box,.error-ai-response) { background: var(--ui-ai-soft) !important; padding: 24px !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; font-size: 1rem !important; color: var(--ui-text) !important; }
    body .detective-form .field-label::before { display: none !important; }
    body.game-page :is(.solo-match-dialog,.solo-player-card,.solo-match-card,.solo-leaderboard-card,.solo-vs-page,.room-battle-page) { background: var(--ui-surface) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; box-shadow: var(--ui-shadow) !important; }
    body.game-page :is(#matchmakingHint,#matchmakingTitle,.solo-rank-name,.solo-match-dialog p) { color: var(--ui-text) !important; }
    body.game-page #matchCountdown { color: var(--ui-text) !important; font-size: 2rem !important; }
    body.game-page :is(.speaker-head span,.topic-sides span,.argument-skill-row span,.voice-status,.mode-button,.rank-token,.rank-badge span,.vs-player span,.main-nav a) { color: var(--ui-secondary) !important; }
    body.game-page :is(.ui-back,.ui-menu-toggle,.button.secondary,.button.ui-secondary-action) { color: var(--ui-link) !important; }
    body.game-page :is(.solo-match-dialog,.solo-vs-page) :is(strong,span) { color: var(--ui-text) !important; }
    body .admin-form { gap: 16px !important; }
    body .admin-form input,body .admin-form select { width: 100% !important; }
    body .ui-metrics { display: grid !important; grid-template-columns: repeat(3,minmax(0,1fr)) !important; gap: 16px !important; margin-bottom: 32px !important; }
    body .ui-metric { border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; background: var(--ui-surface) !important; padding: 24px !important; }
    body .ui-metric strong { display: block !important; font-size: 2rem !important; color: var(--ui-primary) !important; }
    body .ui-metric span { font-size: .875rem !important; color: var(--ui-secondary) !important; }
    body .gemini-output { min-height: 100px !important; background: var(--ui-dark-bg) !important; color: var(--ui-dark-text) !important; border-radius: var(--ui-radius-card) !important; padding: 24px !important; white-space: pre-wrap !important; overflow-wrap: anywhere !important; }
    body .gemini-output:empty::before { content: 'Chưa có phản hồi. Gửi câu hỏi thử để kiểm tra kết nối AI.' !important; }
    body .opponent-transcript:empty::before { content: 'Đối thủ đang soạn…' !important; display: block !important; padding: 32px !important; color: var(--ui-secondary) !important; border: 1px dashed var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body #debateTimer { font-size: 2rem !important; color: var(--ui-text) !important; font-variant-numeric: tabular-nums !important; }
    body .radar-chart svg text { fill: var(--ui-secondary) !important; font-family: var(--ui-font) !important; }
    body .radar-chart svg polygon:last-of-type { fill: var(--ui-ring) !important; stroke: var(--ui-primary) !important; }
    body .radar-chart svg circle { fill: var(--ui-primary) !important; }
    body #argumentScore { font-size: 2rem !important; color: var(--ui-success-text) !important; padding: 12px 20px !important; border-radius: var(--ui-radius-pill) !important; background: var(--ui-success-soft) !important; }
    body .argument-source { padding: 24px !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; margin-bottom: 24px !important; }
    body.game-page :is(.debate-arena,.debate-speaker,.debate-topic,.matching-panel,.room-matching-card,.vs-stage) { background: var(--ui-surface) !important; color: var(--ui-text) !important; border-color: var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; }
    body input[type=range] { accent-color: var(--ui-primary) !important; width: 100% !important; min-height: 44px !important; }
    body .ui-range-value { font-size: 1.75rem !important; font-weight: 700 !important; color: var(--ui-primary) !important; display: block !important; }
    body .ui-character-count { display: block !important; text-align: right !important; color: var(--ui-muted) !important; font-size: .8125rem !important; margin: 4px 0 12px !important; }
    body .ui-toast { position: fixed !important; top: 92px !important; right: 24px !important; max-width: min(420px,calc(100vw - 32px)) !important; z-index: 140 !important; background: var(--ui-surface) !important; border: 1px solid var(--ui-border) !important; border-left: 4px solid var(--ui-success) !important; border-radius: var(--ui-radius-control) !important; padding: 16px 24px !important; box-shadow: var(--ui-shadow-raised) !important; }
    body .ui-loading::after { content: '' !important; display: inline-block !important; width: 14px !important; height: 14px !important; border: 2px solid currentColor !important; border-right-color: transparent !important; border-radius: var(--ui-radius-pill) !important; animation: ui-spin 800ms linear infinite !important; margin-left: 8px !important; }
    body [hidden] { display: none !important; }
    body.game-page :is(.app-panel,.arena-card,.battle-panel,.debate-panel,.matching-card,.vs-card,.room-card) { background: var(--ui-surface) !important; color: var(--ui-text) !important; border: 1px solid var(--ui-border) !important; border-radius: var(--ui-radius-card) !important; box-shadow: var(--ui-shadow) !important; }
    body.game-page :is(.matching-title,.matching-status,.battle-timer,.countdown,.debate-timer) { color: var(--ui-text) !important; font-variant-numeric: tabular-nums !important; }
    body.game-page :is(.battle-timer,.countdown,.debate-timer) { font-size: 2rem !important; }
    @media (max-width: 1100px) {
        body .assignment-task-grid { grid-template-columns: repeat(2,minmax(0,1fr)) !important; }
    }
    @media (max-width: 1023px) {
        body .app-shell { display: block !important; padding: 24px !important; }
        body .app-shell > .app-sidebar { display: none !important; position: fixed !important; top: 84px !important; left: 16px !important; bottom: 16px !important; z-index: 80 !important; max-height: calc(100dvh - 100px) !important; box-shadow: var(--ui-shadow-raised) !important; }
        body .app-shell > .app-sidebar.ui-drawer-open { display: flex !important; }
        body :is(.assignment-workspace,.prompt-workspace,.detective-layout,.argument-workspace,.socratic-workspace,.gemini-grid,.profile-grid,.teacher-grid) { grid-template-columns: 1fr !important; }
        body :is(.ui-review-grid,.trust-layout,.human-first-grid,.error-layout) { grid-template-columns: 1fr !important; }
    }
    @media (min-width: 1024px) {
        body .ui-menu-toggle { display: none !important; }
        body .ui-menu-toggle.ui-module-menu { display: block !important; }
    }
    @media (max-width: 767px) {
        body .site-header { height: 68px !important; padding: 12px 16px !important; gap: 8px !important; }
        body .brand { font-size: .875rem !important; gap: 8px !important; }
        body .main-nav { display: none !important; }
        body .header-actions { margin-left: auto !important; }
        body .account-menu { min-width: 0 !important; max-width: 140px !important; font-size: .8125rem !important; }
        body .account-menu summary { overflow-wrap: anywhere !important; }
        body .app-shell,body .app-shell.module-shell { padding: 24px 16px !important; }
        body h1,body .workshop-hero h1 { font-size: 1.5rem !important; }
        body :is(.app-panel,.workshop-card,.compare-card,.detective-task,.detective-form,.piece-tray,.argument-canvas,.thinking-board,.socratic-chat-panel) { padding: 20px !important; }
        body :is(.assignment-task-grid,.compare-grid,.assignment-writing-grid,.ui-metrics) { grid-template-columns: 1fr !important; }
        body .compare-package-list { grid-template-columns: 1fr !important; }
        body :is(.hero-stamp,.hero-symbol) { display: none !important; }
        body .hero-skills { gap: 8px !important; }
        body .socratic-stagebar { display: grid !important; grid-template-columns: repeat(2,minmax(0,1fr)) !important; }
        body .auth-card { padding: 24px !important; }
        body .assignment-consent-card { padding: 24px !important; }
        body .radar-chart { min-height: 0 !important; }
        body .assignment-chatbot { width: 100% !important; max-width: 100% !important; }
        body .assignment-chat-panel { max-width: calc(100vw - 32px) !important; }
        body .assignment-timer { width: 100% !important; }
        body .assignment-task-box { min-height: 180px !important; }
        body .ui-toolbar label { width: 100% !important; justify-content: space-between !important; }
    }
    @media (prefers-reduced-motion: reduce) {
        body *,body *::before,body *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
    }
}
@keyframes ui-spin { to { transform: rotate(360deg); } }

```

## app/static/js/design-system.js

```js
/* Presentation enhancements only: no API calls or changes to learning state. */
(() => {
    'use strict';
    const make = (tag, className, text) => {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text) node.textContent = text;
        return node;
    };
    const content = document.querySelector('.app-content');
    const sidebar = document.querySelector('.app-shell > .app-sidebar');
    if (content) {
        const breadcrumb = make('nav', 'ui-breadcrumb');
        breadcrumb.setAttribute('aria-label', 'Đường dẫn trang');
        const back = make('a', 'ui-back', '← Trang chủ');
        back.href = '/app';
        breadcrumb.append(back, make('span', '', '/'), make('span', '', content.querySelector('h1')?.textContent.trim() || 'Không gian học tập'));
        content.prepend(breadcrumb);
    }
    if (sidebar) {
        sidebar.id ||= 'uiNavigation';
        const toggle = make('button', 'ui-menu-toggle', '☰ Danh mục');
        if (sidebar.closest('.module-shell')) toggle.classList.add('ui-module-menu');
        toggle.type = 'button';
        toggle.setAttribute('aria-controls', sidebar.id);
        toggle.setAttribute('aria-expanded', 'false');
        document.querySelector('.header-actions')?.prepend(toggle);
        const close = () => { sidebar.classList.remove('ui-drawer-open'); toggle.setAttribute('aria-expanded', 'false'); };
        toggle.addEventListener('click', () => {
            const open = sidebar.classList.toggle('ui-drawer-open');
            toggle.setAttribute('aria-expanded', String(open));
        });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
        document.addEventListener('click', e => { if (!sidebar.contains(e.target) && !toggle.contains(e.target)) close(); });
    }
    // The existing select remains the sole submitted authentication role.
    const role = document.querySelector('#role');
    if (role) {
        const choices = make('div', 'ui-role-tabs');
        choices.setAttribute('role', 'group');
        choices.setAttribute('aria-label', 'Vai trò đăng nhập');
        [...role.options].forEach(option => {
            const button = make('button', '', option.value === 'admin' ? 'Quản trị' : option.textContent);
            button.type = 'button';
            button.setAttribute('aria-pressed', String(role.value === option.value));
            button.addEventListener('click', () => {
                role.value = option.value;
                role.dispatchEvent(new Event('change', {bubbles: true}));
                [...choices.children].forEach(child => child.setAttribute('aria-pressed', String(child === button)));
            });
            choices.append(button);
        });
        role.before(choices);
        role.hidden = true;
        document.querySelector('label[for=role]')?.setAttribute('hidden', '');
    }
    document.querySelectorAll('textarea').forEach((input, index) => {
        const counter = make('output', 'ui-character-count');
        counter.id = `uiCharacterCount${index}`;
        const update = () => { counter.textContent = `${input.value.length.toLocaleString('vi-VN')} ký tự`; };
        input.after(counter);
        update();
        input.addEventListener('input', update);
    });
    document.querySelectorAll('input[type=range]').forEach(input => {
        const output = make('output', 'ui-range-value', input.value);
        const update = () => { output.textContent = input.value; };
        input.after(output);
        input.addEventListener('input', update);
    });
    // Search and sorting are local to each visible collection; no data is fabricated.
    const lists = '.assignment-task-grid,.compare-package-list,.student-table,.teacher-topic-list,.assignment-submission-list,.compare-submission-list,.report-list,.teacher-account-list';
    document.querySelectorAll(lists).forEach((list, index) => {
        const rows = [...list.children].filter(node => node.matches('a,article') && !node.matches('.assignment-empty,.ui-empty'));
        if (rows.length < 2 || list.closest('.assignment-list-page')?.querySelector('#assignmentSearch')) return;
        const toolbar = make('div', 'ui-toolbar');
        const input = make('input');
        input.type = 'search'; input.placeholder = 'Tìm theo tên hoặc nội dung…';
        input.setAttribute('aria-label', 'Tìm trong danh sách');
        const sortLabel = make('label', '', 'Sắp xếp');
        const sort = make('select');
        sort.setAttribute('aria-label', 'Sắp xếp danh sách');
        [['default','Ban đầu'],['asc','Tên A → Z'],['desc','Tên Z → A']].forEach(([value,label]) => {
            const option = make('option', '', label); option.value = value; sort.append(option);
        });
        sortLabel.append(sort);
        const count = make('span', 'ui-result-count');
        count.setAttribute('role', 'status');
        const empty = make('div', 'ui-empty', 'Không có kết quả phù hợp. Hãy thử từ khóa khác.');
        const reset = make('button', 'button secondary', 'Xóa tìm kiếm'); reset.type = 'button';
        empty.append(make('br'), reset); empty.hidden = true;
        list.after(empty);
        const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').toLocaleLowerCase('vi');
        const update = () => {
            const query = normalize(input.value.trim());
            let visible = 0;
            rows.forEach(row => { row.hidden = !normalize(row.textContent).includes(query); if (!row.hidden) visible++; });
            count.textContent = `${visible} / ${rows.length} mục`;
            empty.hidden = visible !== 0;
        };
        input.addEventListener('input', update);
        reset.addEventListener('click', () => { input.value = ''; update(); input.focus(); });
        sort.addEventListener('change', () => {
            const sorted = [...rows];
            if (sort.value !== 'default') sorted.sort((a,b) => {
                const name = node => (node.querySelector('strong,h3') || node).textContent.trim();
                return name(a).localeCompare(name(b), 'vi') * (sort.value === 'desc' ? -1 : 1);
            });
            sorted.forEach(row => list.append(row));
        });
        toolbar.append(input, sortLabel, count); list.before(toolbar); update();
    });
    // Add persistent labels to older teacher forms that relied on placeholders.
    document.querySelectorAll('.admin-form input:not([type=hidden]),.admin-form textarea,.admin-form select').forEach((input,index) => {
        if (input.closest('label') || (input.id && document.querySelector(`label[for="${CSS.escape(input.id)}"]`))) return;
        input.id ||= `uiField${index}`;
        const names = {teacher_score:'Điểm giáo viên', teacher_review:'Nhận xét giáo viên', title:'Tiêu đề', side_a:'Quan điểm A', side_b:'Quan điểm B', criteria:'Tiêu chí đánh giá', question:'Câu hỏi', prompt:'Đề bài', rubric:'Tiêu chí chấm', name:'Họ và tên', username:'Tên đăng nhập', password:'Mật khẩu', code:'Mã bài', field:'Lĩnh vực', text:'Nội dung', task:'Nhiệm vụ', error_type:'Loại lỗi'};
        const label = make('label', 'field-label', input.placeholder || names[input.name] || 'Nội dung cấu hình');
        label.htmlFor = input.id;
        const wrapper = make('div', 'ui-field');
        input.before(wrapper); wrapper.append(label, input);
    });
    document.querySelectorAll('button').forEach(button => {
        if (/^Xóa(?:\s|$)/.test(button.textContent.trim()) || button.querySelector('[data-lucide="trash-2"]')) button.dataset.uiDanger = '';
    });
    document.querySelectorAll('.assignment-review-body').forEach(body => {
        const form = body.querySelector('form');
        if (!form) return;
        const answer = make('section','ui-review-answer');
        [...body.childNodes].filter(node => node !== form).forEach(node => answer.append(node));
        const grid = make('div','ui-review-grid');
        grid.append(answer,form); body.append(grid);
    });
    document.querySelectorAll('.assignment-task-form').forEach(form => {
        const preview = make('details','ui-preview');
        const title = make('h3');
        const prompt = make('p');
        const rubric = make('p');
        preview.append(make('summary','','Xem trước nội dung nhiệm vụ'),title,prompt,make('h3','','Tiêu chí chấm'),rubric);
        form.after(preview);
        const update = () => {
            title.textContent = form.elements.title?.value || 'Tên nhiệm vụ';
            prompt.textContent = form.elements.prompt?.value || 'Nội dung đề bài sẽ hiển thị ở đây.';
            rubric.textContent = form.elements.rubric?.value || 'Chưa nhập tiêu chí chấm.';
        };
        form.addEventListener('input',update); update();
        const submit = form.querySelector('button[type=submit]');
        if (submit) {
            const actions = make('div','ui-form-actions');
            submit.before(actions);
            const cancel = make('button','button secondary','Đóng biểu mẫu'); cancel.type = 'button';
            cancel.addEventListener('click',() => { const details = form.closest('details'); if (details) details.open = false; });
            actions.append(cancel,submit);
        }
    });
    document.querySelectorAll('.muted-note').forEach(note => {
        if (note.textContent.trim().startsWith('Chưa có')) note.classList.add('ui-empty');
    });
    // Existing async handlers own disabled state. Reflect that state visually.
    const loadingObserver = new MutationObserver(records => {
        records.forEach(({target}) => {
            target.classList.toggle('ui-loading', target.disabled && /đang|chờ|gửi|chấm|kiểm tra/i.test(target.textContent));
            target.setAttribute('aria-busy', String(target.classList.contains('ui-loading')));
        });
    });
    document.querySelectorAll('button[type=submit]').forEach(button => loadingObserver.observe(button, {attributes: true, attributeFilter: ['disabled']}));
    // Consent can be dismissed by leaving the exercise, without bypassing consent.
    const modal = document.querySelector('#assignmentConsent');
    if (modal) {
        const card = modal.querySelector('.assignment-consent-card');
        const leave = modal.querySelector('a');
        const close = make('a', 'ui-back', 'Đóng');
        close.href = leave?.href || '/app'; close.setAttribute('aria-label', 'Đóng và quay lại danh sách nhiệm vụ');
        card.prepend(close);
        modal.addEventListener('keydown', event => {
            if (event.key === 'Escape') { event.preventDefault(); close.click(); }
            if (event.key !== 'Tab') return;
            const nodes = [...modal.querySelectorAll('a,button:not(:disabled),input,textarea,select')].filter(node => node.getClientRects().length);
            const first = nodes[0], last = nodes[nodes.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        });
        const focus = () => { if (!modal.hidden) close.focus(); choosePrimary(); };
        new MutationObserver(focus).observe(modal, {attributes:true, attributeFilter:['hidden']});
        focus();
    }
    document.querySelectorAll('main > .app-panel[role=alert]').forEach(message => {
        // Keep the original message accessible in the document after the toast fades.
        const toast = make('div','ui-toast',message.textContent);
        toast.setAttribute('role','status'); document.body.append(toast);
        window.setTimeout(() => toast.remove(),4000);
    });
    document.querySelectorAll('img').forEach(img => { img.loading ||= 'lazy'; img.decoding = 'async'; });
    const iconNames = {'bulb':'lightbulb','book-2':'book-open','help-circle':'circle-help','question-mark':'help-circle','message-question':'message-circle-question','refresh':'refresh-cw','stack-2':'layers','edit':'pencil','alert-triangle':'triangle-alert','map-2':'map','flag-2':'flag'};
    document.querySelectorAll('i.ti').forEach(icon => {
        const name = [...icon.classList].find(item => item.startsWith('ti-'))?.slice(3);
        if (!name) return;
        icon.removeAttribute('class');
        icon.setAttribute('data-lucide',iconNames[name] || name);
    });
    if (window.lucide) window.lucide.createIcons({attrs:{'stroke-width':1.75,'aria-hidden':'true'}});
    function choosePrimary() {
        const buttons = [...document.querySelectorAll('.button.primary')].filter(node => node.getClientRects().length && !node.closest('.assignment-consent[hidden]'));
        const featured = buttons.find(node => node.closest('.assignment-consent:not([hidden])')) || buttons.find(node => node.matches('#assignmentForm button[type=submit],#promptForm button[type=submit],#socraticForm button[type=submit]')) || buttons[0];
        buttons.forEach(node => node.classList.toggle('ui-secondary-action',node !== featured));
    }
    choosePrimary();
    document.querySelectorAll('details').forEach(details => details.addEventListener('toggle',choosePrimary));
    document.addEventListener('assignment:submitted',choosePrimary);
})();

```

## scripts/verify_redesign.py

```py
"""Browser review on a temporary runtime copy; never calls the AI provider."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.services.storage import data_dir
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server, WSGIRequestHandler


class Quiet(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


def run():
    output = Path('artifacts/ui-redesign')
    output.mkdir(parents=True, exist_ok=True)
    original = create_app()
    with original.app_context():
        source = Path(data_dir())
    catalog = json.loads(Path('anh_giao_dien_website_2026-10-24/danh-muc.json').read_text(encoding='utf-8'))
    screens = [r for r in catalog['screens'] if r['device'] == 'desktop']
    # States sharing a URL are checked separately by the existing functional tests.
    routes = list({(r['role'], r['route']): r for r in screens}.values())
    state_review = '--states' in sys.argv
    if state_review:
        routes = [r for r in routes if r['id'] in ['11-nhiem-vu-mo-chat-ai','16-prompt-phan-bien','33-gv-mo-bai-nop','34-gv-mo-form-sua-nhiem-vu','35-quan-tri','43-dau-truong-lap-luan-battle','02-dang-nhap-hoc-sinh']]
    results, errors = [], []
    with tempfile.TemporaryDirectory(prefix='ui-review-') as temp:
        for file in source.glob('*.json'):
            shutil.copy2(file, Path(temp) / file.name)
        app = create_app()
        app.config.update(DATA_DIR=temp, TESTING=True, GEMINI_API_KEYS=[])
        auth = json.loads((Path(temp) / 'auth.json').read_text(encoding='utf-8'))
        student = next(s for s in auth['students'] if s.get('account_import_batch') == 'capnhat-simulation-v1')
        sessions = {
            'public': {},
            'student': {'role':'student', 'student_username':student['username'], 'student_name':student['name']},
            'teacher': {'role':'teacher', 'teacher_username':student['teacher_username'], 'teacher_name':'Giáo viên'},
            'bank_teacher': {'role':'teacher', 'teacher_username':'teacher01', 'teacher_name':'Giáo viên'},
            'admin': {'role':'admin', 'admin_username':'admin'},
        }
        server = make_server('127.0.0.1', 0, app, threaded=True, request_handler=Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                for width in ([360, 1440] if state_review else [360, 768, 1024, 1440]):
                    contexts = {}
                    for screen in routes:
                        role = screen['role']
                        if role not in contexts:
                            context = browser.new_context(viewport={'width':width,'height':1000}, reduced_motion='reduce')
                            if sessions[role]:
                                value = app.session_interface.get_signing_serializer(app).dumps(sessions[role])
                                context.add_cookies([{'name':'session','value':value,'url':base}])
                            page = context.new_page()
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            contexts[role] = (context,page)
                        page = contexts[role][1]
                        response = page.goto(base + screen['route'], wait_until='networkidle')
                        if state_review:
                            if screen['id'] == '11-nhiem-vu-mo-chat-ai':
                                modal = page.locator('#assignmentConsent')
                                if modal.is_visible():
                                    page.locator('#acceptAssignmentConsent').click()
                                    page.wait_for_function("document.querySelector('.assignment-page').classList.contains('is-consent-accepted')")
                                page.locator('#assignmentAnswer').fill('Bài làm kiểm tra giao diện trên bản sao dữ liệu.')
                                page.locator('#assignmentSaveDraft').click()
                                assert page.locator('#assignmentDraftStatus').inner_text()
                            if screen['id'] == '34-gv-mo-form-sua-nhiem-vu':
                                page.locator('#newAssignment').evaluate('(element) => element.open = true')
                                form = page.locator('#newAssignment .assignment-task-form')
                                form.locator('[name=title]').fill('Bản xem trước giao diện')
                                page.locator('#newAssignment .ui-preview').evaluate('(element) => element.open = true')
                                actual = page.locator('#newAssignment .ui-preview h3').first.inner_text()
                                assert actual == 'Bản xem trước giao diện', repr({'preview':actual,'errors':errors})
                            if screen['id'] == '33-gv-mo-bai-nop':
                                page.locator('.teacher-topic-editor').first.evaluate('(element) => element.open = true')
                                assert page.locator('.ui-review-grid').first.is_visible()
                            page.screenshot(path=str(output / f"{width}-{screen['id']}-state.png"),full_page=False)
                        info = page.evaluate('''() => ({width:innerWidth, document:document.documentElement.scrollWidth,
                            overflow:[...document.querySelectorAll('main *')].filter(e => e.getClientRects().length && e.getBoundingClientRect().right > innerWidth + 2).slice(0,8).map(e => e.tagName+'.'+e.className),
                            primary:[...document.querySelectorAll('.button.primary')].filter(e=>e.getClientRects().length).length,
                            color:document.querySelector('.button.primary') ? getComputedStyle(document.querySelector('.button.primary')).backgroundColor:null})''')
                        results.append({'id':screen['id'],'route':screen['route'],'width':width,'status':response.status,**info})
                        if screen['id'] in ['01-trang-chu','02-dang-nhap-hoc-sinh','08-danh-sach-nhiem-vu','16-prompt-phan-bien','24-gv-tong-quan','30-gv-bai-nop','35-quan-tri','43-dau-truong-lap-luan-battle'] and width in [360,1440]:
                            page.screenshot(path=str(output / f"{width}-{screen['id']}.png"),full_page=False)
                        if screen['id'] == '02-dang-nhap-hoc-sinh':
                            page.get_by_role('button',name='Giáo viên',exact=True).click()
                            assert page.locator('#role').input_value() == 'teacher'
                        if screen['id'] == '19-ban-do-kho-bai':
                            search = page.get_by_role('searchbox',name='Tìm trong danh sách')
                            search.fill('zzzz-no-match')
                            assert page.locator('.ui-empty').is_visible()
                        if screen['id'] == '24-gv-tong-quan' and width == 360:
                            page.get_by_role('button',name='Danh mục').click()
                            assert page.locator('.app-sidebar').is_visible()
                            page.keyboard.press('Escape')
                            assert not page.locator('.app-sidebar').is_visible()
                    print(f'Checked {width}px: {len(routes)} routes',flush=True)
                    for context,_ in contexts.values():
                        context.close()
                browser.close()
            with app.test_client() as client:
                for home in ['/', '/app']:
                    html = client.get(home).get_data(as_text=True)
                    assert 'css/design-system.css' not in html
                    assert 'css/design-tokens.css' not in html
                    assert 'js/design-system.js' not in html
        finally:
            server.shutdown()
            thread.join()
    report = {'checks':results,'browser_errors':errors,'horizontal_overflow':[r for r in results if r['document'] > r['width']+2]}
    (output/('state-review.json' if state_review else 'browser-review.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(results),'errors':errors,'overflow':len(report['horizontal_overflow'])},ensure_ascii=False))


if __name__ == '__main__':
    run()

```