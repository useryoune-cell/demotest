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
