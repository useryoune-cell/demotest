/* Presentation helpers for the learning workshops. AI scoring stays on the server. */
(() => {
    const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').toLowerCase();
    const promptForm = document.getElementById('promptCriticForm');
    if (promptForm) {
        const input = document.getElementById('criticPrompt');
        const scenario = document.getElementById('promptScenario');
        const rewrite = document.getElementById('promptRewrite');
        let lastReviewed = '';
        const steps = [
            ['role', 'Vai trò', /dong vai|vai tro|chuyen gia|nha nghien cuu|nguoi kiem chung|historian|act as/],
            ['verify', 'Kiểm chứng', /kiem chung|doi chieu|xac minh|kiem tra|bang chung|can cu|nguon|verify|evidence/],
            ['counter', 'Phản biện', /phan bien|trai chieu|doi lap|phan bac|gia dinh|han che|counter|opposing/],
            ['conclude', 'Kết luận lại', /ket luan|dieu chinh|chac chan|chua du|dieu kien|revise|conclusion|uncertain/],
        ];
        function updateStructure() {
            const text = normalize(input.value);
            let count = 0;
            for (const [key, label, pattern] of steps) {
                const present = pattern.test(text);
                count += Number(present);
                const chip = document.querySelector(`[data-prompt-step="${key}"]`);
                chip.classList.toggle('present', present);
                chip.textContent = `${present ? '✓' : '○'} ${label}`;
            }
            document.getElementById('promptWordCount').textContent = `${input.value.trim() ? input.value.trim().split(/\s+/).length : 0} từ`;
            document.getElementById('promptStructureCount').textContent = `${count}/4 bước`;
            document.getElementById('promptStructureProgress').style.width = `${count * 25}%`;
        }
        input.addEventListener('input', updateStructure);
        scenario.addEventListener('change', () => {
            document.getElementById('promptSituation').textContent = scenario.selectedOptions[0].dataset.task;
            document.getElementById('promptRubric').hidden = true;
            document.getElementById('promptSuggestion').hidden = true;
            document.getElementById('promptPrevious').hidden = true;
            document.getElementById('promptFeedbackEmpty').hidden = false;
            document.getElementById('promptScoreMeta').textContent = 'Đã đổi tình huống. Em có thể điều chỉnh prompt đang viết.';
            rewrite.disabled = true;
            lastReviewed = '';
        });
        promptForm.addEventListener('prompt:reviewed', event => {
            lastReviewed = event.detail.prompt;
            rewrite.disabled = false;
            document.getElementById('promptFeedbackEmpty').hidden = true;
        });
        rewrite.addEventListener('click', () => {
            document.getElementById('promptPreviousText').textContent = lastReviewed;
            document.getElementById('promptPrevious').hidden = false;
            document.getElementById('promptScoreMeta').textContent = 'Giữ ý tốt, bổ sung yêu cầu còn thiếu rồi phân tích lại.';
            input.focus();
            input.setSelectionRange(input.value.length, input.value.length);
            rewrite.disabled = true;
        });
        updateStructure();
    }

    const search = document.getElementById('assignmentSearch');
    if (search) {
        const cards = [...document.querySelectorAll('[data-task-topic]')];
        const filters = [...document.querySelectorAll('[data-task-filter]')];
        let current = 'all';
        function filter() {
            const query = normalize(search.value.trim());
            let count = 0;
            for (const card of cards) {
                card.hidden = !(current === 'all' || current === card.dataset.taskTopic) || !normalize(card.textContent).includes(query);
                count += Number(!card.hidden);
            }
            document.getElementById('assignmentListCount').textContent = `${count} nhiệm vụ`;
            document.getElementById('assignmentSearchEmpty').hidden = count > 0 || cards.length === 0;
        }
        filters.forEach(button => button.addEventListener('click', () => {
            current = button.dataset.taskFilter;
            filters.forEach(item => { item.classList.toggle('active', item === button); item.setAttribute('aria-pressed', String(item === button)); });
            filter();
        }));
        search.addEventListener('input', filter);
        document.getElementById('assignmentClearSearch').addEventListener('click', () => { search.value = ''; filters[0].click(); search.focus(); });
    }

    const assignment = document.querySelector('.assignment-page');
    if (assignment) {
        const input = document.getElementById('assignmentAnswer');
        const status = document.getElementById('assignmentDraftStatus');
        const key = `learning-draft:${assignment.dataset.studentKey}:${assignment.dataset.taskId}`;
        try {
            const saved = JSON.parse(localStorage.getItem(key) || 'null');
            if (saved && typeof saved.answer === 'string') {
                input.value = saved.answer;
                input.dispatchEvent(new Event('input'));
                status.textContent = 'Đã khôi phục nháp trên thiết bị này.';
            }
        } catch { status.textContent = 'Không đọc được bản nháp trên thiết bị này.'; }
        document.getElementById('assignmentSaveDraft').addEventListener('click', () => {
            try {
                localStorage.setItem(key, JSON.stringify({ answer: input.value, saved_at: new Date().toISOString() }));
                status.textContent = 'Đã lưu nháp trên thiết bị này.';
            } catch { status.textContent = 'Chưa lưu được nháp. Em hãy sao chép bài để giữ lại.'; }
        });
        assignment.addEventListener('assignment:submitted', () => {
            try { localStorage.removeItem(key); } catch { /* Submission is already safely on the server. */ }
            status.textContent = 'Bài đã được nộp và lưu.';
        });
    }
})();
