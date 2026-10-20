/* Model output is always inserted as text, never as HTML. */
function renderLearningFeedback(target, data) {
    target.replaceChildren();
    target.classList.add('learning-feedback');
    const line = (tag, text, parent = target) => {
        const el = document.createElement(tag); el.textContent = text; parent.append(el); return el;
    };
    line('h3', `${data.score}/100 · ${data.level || ''}${data.provisional ? ' · Điểm phần đã kiểm tra; tự luận đang chờ đánh giá' : ''}`);
    if (data.choice_feedback) line('p', data.choice_feedback);
    if (data.best) line('p', `Đáp án giáo viên: ${data.best}. ${data.explanation || ''}`);
    if (data.expected_error_type) line('p', `Lỗi chuẩn: ${data.expected_error_type}`);
    for (const row of data.rubric || []) {
        const card = line('article', '');
        line('strong', `${row.label}: ${row.status} · ${row.score}/${row.max}`, card);
        line('p', row.feedback, card);
    }
    line('h4', 'Phản hồi học tập');
    line('p', data.feedback || '');
    if (data.learning_feedback) line('p', data.learning_feedback);
    if (data.reflection) line('p', `Suy nghĩ thêm: ${data.reflection}`);
    target.hidden = false;
}

async function learningPost(url, payload) {
    const response = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Chưa xử lý được yêu cầu.');
    return data;
}

function wireDetectiveFeedback(form) {
    const task = document.getElementById('detectiveTask');
    const meta = document.getElementById('detectiveMeta');
    const result = document.createElement('section');
    result.id = 'detectiveFeedback'; result.setAttribute('aria-live', 'polite'); result.hidden = true;
    form.after(result);
    form.addEventListener('submit', async event => {
        event.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        button.disabled = true; meta.textContent = 'Đang đánh giá từng bước…';
        result.hidden = true;
        const inputs = {suspicious_text: 'detectiveSuspicious', error_type: 'detectiveType', explanation: 'detectiveExplanation', evidence: 'detectiveEvidence', rewrite: 'detectiveRewrite'};
        const payload = {code: task.dataset.code, field: task.dataset.field};
        for (const [key, id] of Object.entries(inputs)) payload[key] = document.getElementById(id).value;
        try {
            const data = await learningPost('/api/modules/detective/score', payload);
            meta.textContent = 'Đã lưu bài; xem nhận xét bên dưới.';
            renderLearningFeedback(result, data);
            const retry = document.createElement('button'); retry.type = 'button'; retry.className = 'button secondary'; retry.textContent = 'Làm lại';
            retry.onclick = () => { result.hidden = true; result.replaceChildren(); meta.textContent = ''; form.scrollIntoView({behavior:'smooth'}); };
            const solution = document.createElement('button'); solution.type = 'button'; solution.className = 'button secondary'; solution.textContent = 'Xem đáp án chuẩn';
            solution.onclick = async () => {
                solution.disabled = true;
                try {
                    const response = await fetch(`/api/modules/detective/solution/${encodeURIComponent(data.submission_id)}`);
                    if (!response.ok) throw new Error('Chưa tải được đáp án.');
                    const answer = await response.json();
                    for (const [key, label] of [['suspicious_text','Đoạn đáng nghi'],['error_type','Loại lỗi'],['evidence','Cách kiểm chứng'],['rewrite','Câu viết lại tham khảo']]) {
                        const p = document.createElement('p'); p.textContent = `${label}: ${answer[key]}`; result.append(p);
                    }
                } catch (error) { meta.textContent = error.message; solution.disabled = false; }
            };
            result.append(retry, solution);
            if (data.passed) {
                const current = [...document.querySelectorAll('[data-station-code]')].find(n => n.dataset.stationCode === task.dataset.code);
                if (current) { current.classList.add('completed'); const next = current.nextElementSibling; if (next) { next.disabled = false; next.classList.add('active'); } }
            }
        } catch (error) { meta.textContent = error.message || 'Mất kết nối, hãy thử lại.'; }
        finally { button.disabled = false; }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const assignment = document.querySelector('.assignment-page');
    const socratic = document.getElementById('socraticChat') || document.querySelector('.socratic-page');
    if (!assignment && !socratic) return;
    const form = document.createElement('form'); form.className = 'app-panel chatbot-rating';
    const label = document.createElement('label'); label.textContent = 'Chatbot giúp em tự suy nghĩ và kiểm chứng đến mức nào? ';
    const select = document.createElement('select'); select.required = true;
    for (let n=1;n<=5;n++) { const o=document.createElement('option'); o.value=n; o.textContent=`${n}/5`; select.append(o); }
    const comment=document.createElement('textarea'); comment.placeholder='Nhận xét hoặc điều cần cải thiện'; comment.maxLength=1000;
    const button=document.createElement('button'); button.className='button secondary'; button.textContent='Gửi đánh giá chatbot';
    const status=document.createElement('p'); status.setAttribute('role','status');
    label.append(select); form.append(label,comment,button,status);
    (assignment || socratic).append(form);
    form.onsubmit=async event=>{event.preventDefault();button.disabled=true;try{await learningPost('/api/chatbot/rating',{module:assignment?'nhiem-vu':'chatbot-socratic',rating:select.value,comment:comment.value});status.textContent='Đã lưu đánh giá.';}catch(error){status.textContent=error.message;}finally{button.disabled=false;}};
});
