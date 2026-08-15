const themeToggle = document.querySelector("[data-theme-toggle]");
const isLandingPage = document.body.classList.contains("landing-page");

function syncThemeToggle() {
    if (!themeToggle) {
        return;
    }

    const isDark = document.documentElement.classList.contains("theme-dark");
    themeToggle.setAttribute("aria-label", isDark ? "Chuyển chế độ sáng" : "Chuyển chế độ tối");
    themeToggle.innerHTML = `<i data-lucide="${isDark ? "sun" : "moon"}"></i>`;
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

if (themeToggle && !isLandingPage) {
    syncThemeToggle();
    themeToggle.addEventListener("click", () => {
        const isDark = document.documentElement.classList.toggle("theme-dark");
        try {
            localStorage.setItem("ct-theme", isDark ? "dark" : "light");
        } catch (error) {
            document.documentElement.classList.toggle("theme-dark", isDark);
        }
        syncThemeToggle();
    });
}

if (window.lucide) {
    window.lucide.createIcons();
}

if (document.body.classList.contains("landing-page")) {
    document.querySelectorAll(".button.primary").forEach((button) => {
        button.animate(
            [
                { backgroundPosition: "0% 50%" },
                { backgroundPosition: "100% 50%" },
                { backgroundPosition: "0% 50%" },
            ],
            {
                duration: 7000,
                iterations: Infinity,
                easing: "ease-in-out",
            },
        );
    });
}

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                revealObserver.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.18 },
);

document.querySelectorAll(".reveal").forEach((node) => revealObserver.observe(node));

const countObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                return;
            }

            const target = Number(entry.target.dataset.count || "0");
            const started = performance.now();
            const duration = 900;

            function tick(now) {
                const progress = Math.min((now - started) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                entry.target.textContent = Math.round(target * eased);
                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            requestAnimationFrame(tick);
            countObserver.unobserve(entry.target);
        });
    },
    { threshold: 0.7 },
);

document.querySelectorAll("[data-count]").forEach((node) => countObserver.observe(node));

document.querySelectorAll(".module-avatar").forEach((image) => {
    const showModuleFallback = () => {
        image.hidden = true;
        const fallback = image.nextElementSibling;
        if (fallback?.classList.contains("module-avatar-fallback")) {
            fallback.hidden = false;
        }
        if (window.lucide) {
            window.lucide.createIcons();
        }
    };
    image.addEventListener("error", showModuleFallback);
    if (image.complete && image.naturalWidth === 0) {
        showModuleFallback();
    }
});

document.querySelectorAll(".ecosystem-image-frame img").forEach((image) => {
    const showEcosystemFallback = () => {
        image.hidden = true;
        const fallback = image.nextElementSibling;
        if (fallback?.classList.contains("ecosystem-icon-fallback")) {
            fallback.hidden = false;
        }
        if (window.lucide) {
            window.lucide.createIcons();
        }
    };
    image.addEventListener("error", showEcosystemFallback);
    if (image.complete && image.naturalWidth === 0) {
        showEcosystemFallback();
    }
});

if (document.body.classList.contains("landing-page")) {
    document
        .querySelectorAll(".feature-strip article, .process-grid article, .area-card, .module-card")
        .forEach((node, index) => {
            node.classList.add("motion-card");
            node.style.setProperty("--stagger", `${Math.min(index * 55, 360)}ms`);
            revealObserver.observe(node);
        });
}

const heroSection = document.querySelector(".hero-section");
if (heroSection) {
    heroSection.addEventListener("pointermove", (event) => {
        const rect = heroSection.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        heroSection.style.setProperty("--hero-x", x.toFixed(3));
        heroSection.style.setProperty("--hero-y", y.toFixed(3));
    });

    heroSection.addEventListener("pointerleave", () => {
        heroSection.style.setProperty("--hero-x", "0");
        heroSection.style.setProperty("--hero-y", "0");
    });
}

const typingNode = document.querySelector("[data-typing]");
if (typingNode) {
    const text = typingNode.dataset.typing;
    let index = 0;

    function typeLoop() {
        typingNode.classList.add("typing-cursor");
        typingNode.textContent = text.slice(0, index);
        index += 1;

        if (index <= text.length) {
            setTimeout(typeLoop, 42);
            return false;
        }

        setTimeout(() => {
            index = 0;
            typeLoop();
        }, 4200);
    }

    typeLoop();
}

const canvas = document.getElementById("argumentCanvas");
if (canvas) {
    const context = canvas.getContext("2d");
    const nodes = [
        { x: 0.2, y: 0.22, color: "#d4af5c", radius: 6 },
        { x: 0.66, y: 0.18, color: "#e3343f", radius: 7 },
        { x: 0.46, y: 0.44, color: "#f0d98a", radius: 8 },
        { x: 0.78, y: 0.62, color: "#b9852e", radius: 7 },
        { x: 0.3, y: 0.76, color: "#d4af5c", radius: 7 },
        { x: 0.58, y: 0.84, color: "#fff8ed", radius: 5 },
    ];
    const links = [
        [0, 2],
        [1, 2],
        [2, 3],
        [2, 4],
        [3, 5],
        [4, 5],
        [0, 4],
    ];
    let mouseX = 0;
    let mouseY = 0;

    canvas.addEventListener("mousemove", (event) => {
        const rect = canvas.getBoundingClientRect();
        mouseX = (event.clientX - rect.left) / rect.width - 0.5;
        mouseY = (event.clientY - rect.top) / rect.height - 0.5;
    });

    function draw(time) {
        const width = canvas.width;
        const height = canvas.height;
        const center = width / 2;
        const pulse = Math.sin(time / 900) * 0.5 + 0.5;

        context.clearRect(0, 0, width, height);
        context.fillStyle = "rgba(12, 9, 4, 0.9)";
        context.fillRect(0, 0, width, height);

        context.strokeStyle = "rgba(240, 216, 138, 0.08)";
        context.lineWidth = 1;
        for (let x = 0; x <= width; x += 54) {
            context.beginPath();
            context.moveTo(x, 0);
            context.lineTo(x, height);
            context.stroke();
        }
        for (let y = 0; y <= height; y += 54) {
            context.beginPath();
            context.moveTo(0, y);
            context.lineTo(width, y);
            context.stroke();
        }

        const projected = nodes.map((node, index) => {
            const drift = Math.sin(time / 1000 + index) * 9;
            return {
                ...node,
                px: node.x * width + drift + mouseX * 18,
                py: node.y * height + Math.cos(time / 1200 + index) * 9 + mouseY * 18,
            };
        });

        links.forEach(([from, to], index) => {
            const a = projected[from];
            const b = projected[to];
            context.strokeStyle = `rgba(240, 216, 138, ${0.16 + pulse * 0.16})`;
            context.lineWidth = index === 2 ? 2.4 : 1.4;
            context.beginPath();
            context.moveTo(a.px, a.py);
            context.lineTo(b.px, b.py);
            context.stroke();
        });

        projected.forEach((node, index) => {
            const radius = node.radius + Math.sin(time / 700 + index) * 1.4;
            context.beginPath();
            context.arc(node.px, node.py, radius * 3.4, 0, Math.PI * 2);
            context.fillStyle = "rgba(240, 216, 138, 0.06)";
            context.fill();

            context.beginPath();
            context.arc(node.px, node.py, radius, 0, Math.PI * 2);
            context.fillStyle = node.color;
            context.fill();

            context.font = "600 14px Space Grotesk, sans-serif";
            context.fillStyle = "rgba(255, 248, 237, 0.8)";
            context.fillText(["Claim", "Counter", "Evidence", "Revise", "Source", "Reflect"][index], node.px + 14, node.py + 5);
        });

        context.beginPath();
        context.arc(center, center, 148 + pulse * 12, 0, Math.PI * 2);
        context.strokeStyle = "rgba(212, 175, 92, 0.22)";
        context.lineWidth = 1.5;
        context.stroke();

        requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
}

const filterTabs = document.querySelectorAll("[data-filter]");
const moduleCards = document.querySelectorAll("[data-area]");
filterTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const filter = tab.dataset.filter;

        filterTabs.forEach((item) => item.classList.toggle("active", item === tab));
        moduleCards.forEach((card) => {
            card.classList.toggle("is-hidden", filter !== "all" && card.dataset.area !== filter);
        });
    });
});

const geminiStatusNode = document.getElementById("geminiStatus");
const geminiOutputNode = document.getElementById("geminiOutput");
const geminiMetaNode = document.getElementById("geminiMeta");
const geminiForm = document.getElementById("geminiTestForm");
const geminiRefreshButton = document.getElementById("refreshGeminiStatus");

async function refreshGeminiStatus() {
    if (!geminiStatusNode) {
        return;
    }

    geminiStatusNode.innerHTML = '<p class="muted-note">Đang tải trạng thái key...</p>';
    try {
        const response = await fetch("/api/gemini/status");
        const data = await response.json();

        if (!data.ok) {
            geminiStatusNode.innerHTML = `<p class="muted-note">${data.error}</p>`;
            return;
        }

        if (!data.keys.length) {
            geminiStatusNode.innerHTML = '<p class="muted-note">Chưa cấu hình key.</p>';
            return;
        }

        geminiStatusNode.innerHTML = data.keys
            .map((key) => {
                const detail = [
                    `requests: ${key.requests_sent}`,
                    `errors: ${key.errors_seen}`,
                    key.cooldown_remaining ? `cooldown: ${key.cooldown_remaining}s` : "",
                    key.last_error ? `last: ${key.last_error}` : "",
                ]
                    .filter(Boolean)
                    .join(" · ");
                return `
                    <article class="key-status-item">
                        <strong>${key.label}</strong>
                        <span class="key-pill ${key.status}">${key.status}</span>
                        <small>${detail || "ready"}</small>
                    </article>
                `;
            })
            .join("");
    } catch (error) {
        geminiStatusNode.innerHTML = `<p class="muted-note">Không tải được trạng thái: ${error}</p>`;
    }
}

if (geminiForm) {
    refreshGeminiStatus();

    geminiForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const prompt = document.getElementById("geminiPrompt").value.trim();

        if (!prompt) {
            geminiOutputNode.textContent = "Bạn cần nhập prompt trước.";
            return;
        }

        geminiOutputNode.textContent = "Đang gọi Gemini...";
        geminiMetaNode.textContent = "";

        try {
            const response = await fetch("/api/gemini/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt }),
            });
            const data = await response.json();

            if (!response.ok) {
                geminiOutputNode.textContent = data.error || "Gemini request failed.";
                await refreshGeminiStatus();
                return;
            }

            geminiOutputNode.textContent = data.text || "(Gemini trả về rỗng)";
            geminiMetaNode.textContent = `${data.model} · ${data.key_label} · ${data.attempts} attempt(s)`;
            await refreshGeminiStatus();
        } catch (error) {
            geminiOutputNode.textContent = `Không gọi được API: ${error}`;
        }
    });
}

if (geminiRefreshButton) {
    geminiRefreshButton.addEventListener("click", refreshGeminiStatus);
}

const socraticForm = document.getElementById("socraticForm");
const socraticInput = document.getElementById("socraticInput");
const socraticThread = document.getElementById("socraticThread");
const socraticMeta = document.getElementById("socraticMeta");
const stagePills = document.querySelectorAll("[data-stage-index]");
const boardSections = document.querySelectorAll("[data-board-key]");
const socraticModeButtons = document.querySelectorAll("[data-socratic-mode]");

const socraticModeIntro = {
    easy: "Em nêu một chủ đề hoặc câu hỏi. Mình sẽ gợi ý từng bước để em tự viết được câu trả lời.",
    advanced: "Em nêu một chủ đề hoặc nhận định. Mình sẽ hỏi sâu để kiểm tra luận điểm, bằng chứng và phản biện của em.",
};

const socraticModeLoading = {
    easy: "Đang chuẩn bị gợi ý từng bước...",
    advanced: "Đang chất vấn lập luận...",
};

const socraticState = {
    mode: "easy",
    stageIndex: 0,
    messages: [
        {
            role: "assistant",
            content: socraticModeIntro.easy,
        },
    ],
    board: {
        claims: [],
        evidence: [],
        unclear: [],
        counterpoints: [],
        revisions: [],
    },
};

function resetSocraticThreadForMode(mode) {
    if (!socraticThread) {
        return;
    }
    const intro = socraticModeIntro[mode] || socraticModeIntro.easy;
    socraticState.mode = mode;
    socraticState.stageIndex = 0;
    socraticState.messages = [{ role: "assistant", content: intro }];
    socraticState.board = {
        claims: [],
        evidence: [],
        unclear: [],
        counterpoints: [],
        revisions: [],
    };
    socraticThread.innerHTML = "";
    appendSocraticMessage("assistant", intro);
    setSocraticStage(0);
    renderBoard();
    socraticMeta.textContent = mode === "advanced" ? "Phiên bản nâng cao" : "Phiên bản dễ tiếp cận";
}

function appendSocraticMessage(role, content, extraClass = "") {
    if (!socraticThread) {
        return null;
    }

    const message = document.createElement("article");
    message.className = `socratic-message ${role === "user" ? "user" : "ai"} ${extraClass}`.trim();

    const label = document.createElement("span");
    label.textContent = role === "user" ? "Em" : "AI";

    const body = document.createElement("p");
    body.textContent = content;

    message.append(label, body);
    socraticThread.appendChild(message);
    socraticThread.scrollTop = socraticThread.scrollHeight;
    return message;
}

function setSocraticStage(stageIndex) {
    socraticState.stageIndex = stageIndex;
    stagePills.forEach((pill) => {
        pill.classList.toggle("active", Number(pill.dataset.stageIndex) === stageIndex);
    });
}

function addBoardUpdates(updates) {
    Object.entries(updates || {}).forEach(([key, values]) => {
        if (!Array.isArray(values)) {
            return;
        }
        values.forEach((value) => {
            if (!value || socraticState.board[key]?.includes(value)) {
                return;
            }
            socraticState.board[key].push(value);
        });
    });
    renderBoard();
}

function addSocraticLabels(labels) {
    const labelMap = {
        "Nhận định": "claims",
        "Bằng chứng": "evidence",
        "Điều chưa rõ": "unclear",
        "Phản biện": "counterpoints",
        "Điều chỉnh": "revisions",
    };
    const updates = {};

    (labels || []).forEach((label) => {
        const key = labelMap[label.type] || "unclear";
        updates[key] = updates[key] || [];
        updates[key].push(label.text);
    });

    addBoardUpdates(updates);
}

function renderBoard() {
    boardSections.forEach((section) => {
        const key = section.dataset.boardKey;
        const container = section.querySelector(".board-items");
        const values = socraticState.board[key] || [];
        container.innerHTML = "";

        if (!values.length) {
            const empty = document.createElement("span");
            empty.className = "board-item empty";
            empty.textContent = "";
            container.appendChild(empty);
            return;
        }

        values.forEach((value) => {
            const item = document.createElement("span");
            item.className = "board-item";
            item.textContent = value;
            container.appendChild(item);
        });
    });
}

if (socraticForm) {
    renderBoard();

    socraticModeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const mode = button.dataset.socraticMode || "easy";
            socraticModeButtons.forEach((item) => item.classList.toggle("active", item === button));
            resetSocraticThreadForMode(mode);
        });
    });

    socraticForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const content = socraticInput.value.trim();
        if (!content) {
            return;
        }

        appendSocraticMessage("user", content);
        socraticState.messages.push({ role: "user", content });
        socraticInput.value = "";
        socraticInput.disabled = true;

        const loading = appendSocraticMessage("assistant", socraticModeLoading[socraticState.mode] || socraticModeLoading.easy, "loading");
        socraticMeta.textContent = "Đang gọi Gemini...";

        try {
            const response = await fetch("/api/modules/socratic/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: socraticState.messages,
                    stage_index: socraticState.stageIndex,
                    board: socraticState.board,
                    mode: socraticState.mode,
                }),
            });
            const data = await response.json();
            loading.remove();

            if (!response.ok) {
                appendSocraticMessage("assistant", data.error || "Không gọi được Gemini.", "error");
                socraticMeta.textContent = "Lỗi Gemini";
                return;
            }

            appendSocraticMessage("assistant", data.ai_message);
            socraticState.messages.push({ role: "assistant", content: data.ai_message });
            setSocraticStage(Number(data.stage_index || 0));
            addBoardUpdates(data.board_updates || {});
            addSocraticLabels(data.labels || []);
            socraticMeta.textContent = `${data.meta.mode_label || "Socratic"} · ${data.stage.key} · ${data.meta.model} · ${data.meta.key_label}`;
        } catch (error) {
            loading.remove();
            appendSocraticMessage("assistant", `Không gọi được API: ${error}`, "error");
            socraticMeta.textContent = "Lỗi kết nối";
        } finally {
            socraticInput.disabled = false;
            socraticInput.focus();
        }
    });
}

const finishSocraticLink = document.getElementById("finishSocraticLink");
if (finishSocraticLink) {
    finishSocraticLink.addEventListener("click", async (event) => {
        const userMessages = socraticState.messages.filter((message) => message.role === "user");
        if (!userMessages.length) {
            sessionStorage.removeItem("reflectionDraft");
            return;
        }

        event.preventDefault();
        socraticMeta.textContent = "Đang tạo bản nháp nhật ký...";

        try {
            const response = await fetch("/api/modules/reflection/draft", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: socraticState.messages,
                    board: socraticState.board,
                    mode: socraticState.mode,
                }),
            });
            const data = await response.json();
            if (response.ok && data.ok) {
                sessionStorage.setItem("reflectionDraft", JSON.stringify(data.draft));
            }
        } catch (error) {
            const latest = userMessages[userMessages.length - 1]?.content || "";
            sessionStorage.setItem("reflectionDraft", JSON.stringify({
                source_module: "chatbot-socratic",
                summary: latest ? `Học sinh vừa trao đổi về: ${latest}` : "Phiên chatbot vừa kết thúc.",
                ai_review: "AI chưa tạo được nhận xét tự động. Em có thể tự ghi điều đã hiểu, điều còn nghi ngờ và điều cần kiểm chứng thêm.",
                student_takeaway: "",
            }));
        } finally {
            window.location.href = finishSocraticLink.href;
        }
    });
}

const humanFirstForm = document.getElementById("humanFirstForm");
const humanQuestion = document.getElementById("humanQuestion");
const humanQuestionHint = document.getElementById("humanQuestionHint");
const humanAnswer = document.getElementById("humanAnswer");
const humanConfidence = document.getElementById("humanConfidence");
const humanConfidenceValue = document.getElementById("humanConfidenceValue");
const humanFirstMeta = document.getElementById("humanFirstMeta");
const humanAiAnswer = document.getElementById("humanAiAnswer");
const humanAiMeta = document.getElementById("humanAiMeta");
const aiLockedState = document.getElementById("aiLockedState");
const humanDecisionPanel = document.getElementById("humanDecisionPanel");
const humanSteps = document.querySelectorAll("[data-human-step]");
const decisionButtons = document.querySelectorAll("[data-decision]");
const decisionReason = document.getElementById("decisionReason");

const humanFirstState = {
    questionId: "",
    studentAnswer: "",
    confidence: 50,
    aiAnswer: "",
    decision: "keep",
};

function setHumanStep(step) {
    humanSteps.forEach((item) => {
        item.classList.toggle("active", Number(item.dataset.humanStep) <= step);
    });
}

if (humanConfidence) {
    humanConfidence.addEventListener("input", () => {
        humanConfidenceValue.textContent = humanConfidence.value;
    });
}

if (humanQuestion) {
    humanQuestion.addEventListener("change", () => {
        const selected = humanQuestion.selectedOptions[0];
        humanQuestionHint.textContent = selected.dataset.hint || "";
    });
}

decisionButtons.forEach((button) => {
    button.addEventListener("click", () => {
        humanFirstState.decision = button.dataset.decision;
        decisionButtons.forEach((item) => item.classList.toggle("active", item === button));
    });
});

if (humanFirstForm) {
    humanFirstForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const answer = humanAnswer.value.trim();

        if (answer.length < 12) {
            humanFirstMeta.textContent = "Câu trả lời cần dài hơn một chút trước khi mở AI.";
            return;
        }

        humanFirstState.questionId = humanQuestion.value;
        humanFirstState.studentAnswer = answer;
        humanFirstState.confidence = Number(humanConfidence.value);
        humanFirstMeta.textContent = "Đã khóa câu trả lời của em. Đang mở AI...";
        humanAnswer.disabled = true;
        humanQuestion.disabled = true;
        humanConfidence.disabled = true;
        setHumanStep(2);

        try {
            const response = await fetch("/api/modules/human-first/ai-answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question_id: humanFirstState.questionId,
                    student_answer: humanFirstState.studentAnswer,
                    confidence: humanFirstState.confidence,
                }),
            });
            const data = await response.json();

            if (!response.ok) {
                humanFirstMeta.textContent = data.error || "Không gọi được Gemini.";
                humanAnswer.disabled = false;
                humanQuestion.disabled = false;
                humanConfidence.disabled = false;
                setHumanStep(1);
                return;
            }

            humanFirstState.aiAnswer = data.ai_answer;
            aiLockedState.hidden = true;
            humanAiAnswer.hidden = false;
            humanAiAnswer.textContent = data.ai_answer;
            humanAiMeta.textContent = `${data.meta.model} · ${data.meta.key_label}`;
            humanDecisionPanel.hidden = false;
            humanFirstMeta.textContent = "AI đã mở. Bây giờ em quyết định giữ hay đổi.";
            setHumanStep(3);
        } catch (error) {
            humanFirstMeta.textContent = `Không gọi được API: ${error}`;
            humanAnswer.disabled = false;
            humanQuestion.disabled = false;
            humanConfidence.disabled = false;
            setHumanStep(1);
        }
    });
}

const goReflectionLink = document.getElementById("goReflectionLink");
if (goReflectionLink) {
    goReflectionLink.addEventListener("click", (event) => {
        const reason = decisionReason?.value.trim() || "";
        if (!reason) {
            event.preventDefault();
            decisionReason.focus();
            humanFirstMeta.textContent = "Em cần giải thích lý do giữ hoặc đổi trước khi hoàn thành.";
            return;
        }

        const context = {
            module: "con-nguoi-truoc-ai-sau",
            question_id: humanFirstState.questionId,
            student_answer: humanFirstState.studentAnswer,
            confidence: humanFirstState.confidence,
            ai_answer: humanFirstState.aiAnswer,
            decision: humanFirstState.decision,
            reason,
        };
        sessionStorage.setItem("humanFirstContext", JSON.stringify(context));
    });
}

const reflectionForm = document.getElementById("reflectionForm");
const reflectionMeta = document.getElementById("reflectionMeta");
const reflectionEntries = document.getElementById("reflectionEntries");
const reflectionSummary = document.getElementById("reflectionSummary");
const reflectionAiReview = document.getElementById("reflectionAiReview");
const reflectionTakeaway = document.getElementById("reflectionTakeaway");

function savedReflectionTitle(entry) {
    const answers = entry.answers || {};
    return answers.takeaway || answers.summary || `${Object.keys(answers).length} mục đã lưu`;
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value || "");
    return div.innerHTML;
}

if (reflectionForm) {
    let reflectionContext = {};
    const draft = JSON.parse(sessionStorage.getItem("reflectionDraft") || "{}");
    const context = JSON.parse(sessionStorage.getItem("humanFirstContext") || "{}");

    if (draft.summary || draft.ai_review) {
        reflectionContext = draft;
        reflectionSummary.textContent = draft.summary || reflectionSummary.textContent;
        reflectionAiReview.textContent = draft.ai_review || reflectionAiReview.textContent;
        reflectionTakeaway.value = draft.student_takeaway || "";
        reflectionMeta.textContent = "Đã nhận bản nháp từ chatbot.";
    } else if (context.student_answer) {
        reflectionContext = {
            source_module: context.module || "con-nguoi-truoc-ai-sau",
            summary: `Học sinh đã trả lời trước: ${context.student_answer}`,
            ai_review: context.ai_answer
                ? `AI đã đưa phản hồi để học sinh so sánh. Quyết định của học sinh: ${context.decision || "chưa ghi"}. Lý do: ${context.reason || "chưa ghi"}.`
                : "Học sinh đã có câu trả lời ban đầu nhưng chưa có phản hồi AI để so sánh.",
        };
        reflectionSummary.textContent = reflectionContext.summary;
        reflectionAiReview.textContent = reflectionContext.ai_review;
        reflectionTakeaway.value = context.reason || "";
    }

    document.querySelectorAll("[data-takeaway-chip]").forEach((button) => {
        button.addEventListener("click", () => {
            const value = button.dataset.takeawayChip || "";
            reflectionTakeaway.value = reflectionTakeaway.value
                ? `${reflectionTakeaway.value.trim()}\n${value}`
                : value;
            reflectionTakeaway.focus();
        });
    });

    reflectionForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const answers = {
            summary: reflectionSummary.textContent.trim(),
            ai_review: reflectionAiReview.textContent.trim(),
            takeaway: reflectionTakeaway.value.trim(),
        };

        reflectionMeta.textContent = "Đang lưu...";
        try {
            const response = await fetch("/api/modules/reflection", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    module: reflectionContext.source_module || context.module || "manual",
                    answers,
                    context: reflectionContext,
                }),
            });
            const data = await response.json();

            if (!response.ok || !data.ok) {
                reflectionMeta.textContent = "Không lưu được nhật ký.";
                return;
            }

            reflectionMeta.textContent = "Đã lưu.";
            sessionStorage.removeItem("reflectionDraft");
            reflectionEntries.innerHTML = data.entries
                .map((entry) => `
                    <article class="reflection-entry">
                        <span>${escapeHtml(entry.module)}</span>
                        <strong>${escapeHtml(savedReflectionTitle(entry))}</strong>
                    </article>
                `)
                .join("");
        } catch (error) {
            reflectionMeta.textContent = `Không gọi được API: ${error}`;
        }
    });
}

const trustInitial = document.getElementById("trustInitial");
const trustRevised = document.getElementById("trustRevised");
const trustInitialValue = document.getElementById("trustInitialValue");
const trustRevisedValue = document.getElementById("trustRevisedValue");
const lockTrustInitial = document.getElementById("lockTrustInitial");
const trustEvidence = document.getElementById("trustEvidence");
const trustRevisedBlock = document.getElementById("trustRevisedBlock");
const trustCard = document.getElementById("trustCard");
const trustQuestion = document.getElementById("trustQuestion");
const trustAiAnswer = document.getElementById("trustAiAnswer");
const scoreTrust = document.getElementById("scoreTrust");
const trustResult = document.getElementById("trustResult");
const trustExplanation = document.getElementById("trustExplanation");
const nextTrustItem = document.getElementById("nextTrustItem");

let trustItem = null;

function updateTrustValues() {
    if (trustInitialValue && trustInitial) {
        trustInitialValue.textContent = trustInitial.value;
    }
    if (trustRevisedValue && trustRevised) {
        trustRevisedValue.textContent = trustRevised.value;
    }
}

async function loadTrustItem(index) {
    if (!trustCard) {
        return;
    }
    const response = await fetch(`/api/modules/trust/item?index=${index}`);
    const data = await response.json();
    trustItem = data.item;
    trustCard.dataset.itemId = trustItem.id;
    trustCard.dataset.index = data.index;
    trustQuestion.textContent = trustItem.question;
    trustAiAnswer.textContent = trustItem.ai_answer;
    trustInitial.disabled = false;
    trustInitial.value = 50;
    trustRevised.value = 50;
    trustEvidence.hidden = true;
    trustRevisedBlock.hidden = true;
    trustResult.hidden = true;
    updateTrustValues();
}

if (trustInitial) {
    trustItem = { id: trustCard.dataset.itemId };
    trustInitial.addEventListener("input", updateTrustValues);
    trustRevised.addEventListener("input", updateTrustValues);
    updateTrustValues();

    lockTrustInitial.addEventListener("click", async () => {
        if (!trustItem.evidence) {
            const response = await fetch(`/api/modules/trust/item?index=${trustCard.dataset.index}`);
            trustItem = (await response.json()).item;
        }
        trustInitial.disabled = true;
        trustEvidence.hidden = false;
        trustEvidence.textContent = trustItem.evidence;
        trustRevisedBlock.hidden = false;
    });

    scoreTrust.addEventListener("click", async () => {
        const response = await fetch("/api/modules/trust/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                item_id: trustCard.dataset.itemId,
                initial: trustInitial.value,
                revised: trustRevised.value,
            }),
        });
        const data = await response.json();
        trustResult.hidden = false;
        document.getElementById("markerInitial").style.left = `${trustInitial.value}%`;
        document.getElementById("markerRevised").style.left = `${trustRevised.value}%`;
        document.getElementById("markerTruth").style.left = `${data.item.ground_truth}%`;
        trustExplanation.textContent = `${data.item.explanation} Điểm hiệu chỉnh: ${data.score.score}/100. Sai lệch sau cùng: ${data.score.revised_error} điểm.`;
    });

    nextTrustItem.addEventListener("click", () => {
        const total = Number(document.querySelector(".trust-layout").dataset.total || "1");
        const next = (Number(trustCard.dataset.index || "0") + 1) % total;
        loadTrustItem(next);
    });
}

const compareForm = document.getElementById("compareForm");
if (compareForm) {
    compareForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const selected = compareForm.querySelector('input[name="bestAnswer"]:checked').value;
        const criteria = document.getElementById("compareCriteria").value.trim();
        const synthesis = document.getElementById("compareSynthesis").value.trim();
        const packageId = compareForm.dataset.packageId || "";
        const response = await fetch("/api/modules/compare/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ package_id: packageId, selected, criteria, synthesis }),
        });
        const data = await response.json();
        document.getElementById("compareMeta").textContent = data.feedback || "Đã lưu bài làm.";
    });
}

const assignmentPage = document.querySelector(".assignment-page");
if (assignmentPage && assignmentPage.dataset.taskId) {
    const taskId = assignmentPage.dataset.taskId;
    const consentModal = document.getElementById("assignmentConsent");
    const acceptConsentButton = document.getElementById("acceptAssignmentConsent");
    const assignmentForm = document.getElementById("assignmentForm");
    const assignmentAnswer = document.getElementById("assignmentAnswer");
    const assignmentMeta = document.getElementById("assignmentMeta");
    const assignmentTimer = document.getElementById("assignmentTimer");
    const assignmentTimerState = document.getElementById("assignmentTimerState");
    const assignmentCounter = document.getElementById("assignmentCounter");
    const assignmentResult = document.getElementById("assignmentResult");
    const assignmentAiReview = document.getElementById("assignmentAiReview");
    const assignmentChatbot = document.getElementById("assignmentChatbot");
    const chatToggle = document.getElementById("assignmentChatToggle");
    const chatClose = document.getElementById("assignmentChatClose");
    const chatPanel = document.getElementById("assignmentChatPanel");
    const chatForm = document.getElementById("assignmentChatForm");
    const chatInput = document.getElementById("assignmentChatInput");
    const chatThread = document.getElementById("assignmentChatThread");
    const assignmentState = {
        attemptId: "",
        startedAt: 0,
        timerId: null,
        chat: [],
    };
    const assignmentSoftLimitSeconds = 45 * 60;

    function formatAssignmentTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
        const rest = Math.floor(seconds % 60).toString().padStart(2, "0");
        return `${minutes}:${rest}`;
    }

    function updateAssignmentTimer() {
        if (!assignmentTimer || !assignmentState.startedAt) {
            return;
        }
        const seconds = Math.max(0, Math.floor((Date.now() - assignmentState.startedAt) / 1000));
        const ratio = Math.min(seconds / assignmentSoftLimitSeconds, 1);
        assignmentTimer.textContent = formatAssignmentTime(seconds);
        if (assignmentTimerState) {
            assignmentTimerState.textContent = seconds >= assignmentSoftLimitSeconds ? "Quá mốc gợi ý" : "Mốc gợi ý 45p";
        }
        assignmentPage.style.setProperty("--assignment-progress", `${ratio * 100}%`);
        assignmentTimer.closest(".assignment-timer")?.classList.toggle("warning", ratio >= 0.8);
    }

    function updateAssignmentCounter() {
        if (!assignmentAnswer || !assignmentCounter) {
            return;
        }
        const text = assignmentAnswer.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        assignmentCounter.textContent = `${words} từ · ${assignmentAnswer.value.length} ký tự`;
    }

    function closeAssignmentChat() {
        if (!assignmentChatbot || !chatPanel || !chatToggle) {
            return;
        }
        assignmentChatbot.classList.remove("is-open");
        assignmentPage.classList.remove("chat-open");
        chatToggle.setAttribute("aria-expanded", "false");
        chatToggle.innerHTML = '<i data-lucide="message-circle"></i>';
        chatPanel.hidden = true;
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    function setAssignmentLocked(locked) {
        assignmentPage.classList.toggle("is-locked", locked);
        document.documentElement.classList.toggle("assignment-modal-open", locked);
        if (locked) {
            closeAssignmentChat();
        }
        if (assignmentForm) {
            assignmentForm.querySelectorAll("textarea, button").forEach((node) => {
                node.disabled = locked;
            });
        }
        if (chatToggle) {
            chatToggle.disabled = locked;
        }
    }

    function appendAssignmentChat(role, content) {
        const article = document.createElement("article");
        article.className = `socratic-message ${role === "student" ? "user" : "ai"}`;
        article.innerHTML = `<span>${role === "student" ? "HS" : "AI"}</span><p></p>`;
        article.querySelector("p").textContent = content;
        chatThread.appendChild(article);
        chatThread.scrollTop = chatThread.scrollHeight;
        assignmentState.chat.push({ role, content });
    }

    async function startAssignmentAttempt() {
        const response = await fetch("/api/modules/assignments/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });
        const data = await response.json();
        if (!response.ok) {
            assignmentMeta.textContent = data.error || "Không bắt đầu được phiên làm bài.";
            return;
        }
        assignmentState.attemptId = data.attempt.id;
        assignmentState.startedAt = data.attempt.started_at ? new Date(data.attempt.started_at).getTime() : Date.now();
        updateAssignmentTimer();
        updateAssignmentCounter();
        assignmentState.timerId = window.setInterval(updateAssignmentTimer, 1000);
        setAssignmentLocked(false);
        assignmentPage.classList.add("is-consent-accepted");
        return true;
    }

    if (assignmentPage.dataset.consent !== "yes") {
        consentModal.hidden = false;
        setAssignmentLocked(true);
    } else {
        startAssignmentAttempt();
    }

    if (acceptConsentButton) {
        acceptConsentButton.addEventListener("click", async () => {
            acceptConsentButton.disabled = true;
            const response = await fetch("/api/modules/assignments/consent", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task_id: taskId }),
            });
            if (response.ok) {
                await startAssignmentAttempt();
                if (assignmentState.attemptId) {
                    consentModal.hidden = true;
                    consentModal.setAttribute("hidden", "");
                } else {
                    acceptConsentButton.disabled = false;
                }
            } else {
                acceptConsentButton.disabled = false;
            }
        });
    }

    if (chatToggle && chatPanel) {
        chatToggle.addEventListener("click", () => {
            if (assignmentPage.classList.contains("is-locked")) {
                return;
            }
            const willOpen = chatPanel.hidden;
            chatPanel.hidden = false;
            assignmentChatbot.classList.toggle("is-open", willOpen);
            assignmentPage.classList.toggle("chat-open", willOpen);
            chatToggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
            chatToggle.innerHTML = `<i data-lucide="${willOpen ? "x" : "message-circle"}"></i>`;
            if (!willOpen) {
                chatPanel.hidden = true;
            } else {
                chatInput.focus();
            }
            if (window.lucide) {
                window.lucide.createIcons();
            }
        });
    }

    if (chatClose && chatPanel) {
        chatClose.addEventListener("click", closeAssignmentChat);
    }

    if (assignmentAnswer) {
        updateAssignmentCounter();
        assignmentAnswer.addEventListener("input", updateAssignmentCounter);
    }

    if (chatForm) {
        chatForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const message = chatInput.value.trim();
            if (!message || !assignmentState.attemptId) {
                return;
            }
            appendAssignmentChat("student", message);
            chatInput.value = "";
            chatInput.disabled = true;
            const loading = document.createElement("article");
            loading.className = "socratic-message ai loading";
            loading.innerHTML = "<span>AI</span><p>Đang trả lời...</p>";
            chatThread.appendChild(loading);

            try {
                const response = await fetch("/api/modules/assignments/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        task_id: taskId,
                        attempt_id: assignmentState.attemptId,
                        message,
                        messages: assignmentState.chat,
                    }),
                });
                const data = await response.json();
                loading.remove();
                appendAssignmentChat("assistant", data.answer || data.error || "AI chưa trả lời được.");
            } catch (error) {
                loading.remove();
                appendAssignmentChat("assistant", `Không gửi được câu hỏi: ${error}`);
            } finally {
                chatInput.disabled = false;
                chatInput.focus();
            }
        });
    }

    if (assignmentForm) {
        assignmentForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const answer = assignmentAnswer.value.trim();
            const durationSeconds = assignmentState.startedAt
                ? Math.max(0, Math.floor((Date.now() - assignmentState.startedAt) / 1000))
                : 0;
            assignmentMeta.textContent = "Đang nộp bài...";
            const response = await fetch("/api/modules/assignments/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_id: taskId,
                    attempt_id: assignmentState.attemptId,
                    answer,
                    chat: assignmentState.chat,
                    duration_seconds: durationSeconds,
                }),
            });
            const data = await response.json();
            if (!response.ok) {
                assignmentMeta.textContent = data.error || "Không nộp được bài.";
                return;
            }
            window.clearInterval(assignmentState.timerId);
            assignmentMeta.textContent = "Đã nộp bài.";
            assignmentAiReview.textContent = data.submission.ai_review;
            assignmentResult.hidden = false;
            closeAssignmentChat();
            assignmentForm.querySelectorAll("textarea, button").forEach((node) => {
                node.disabled = true;
            });
        });
    }
}

const levelButtons = document.querySelectorAll("[data-error-level]");
const errorTask = document.getElementById("errorTask");
const errorQuestion = document.getElementById("errorQuestion");
const errorAiAnswer = document.getElementById("errorAiAnswer");
const errorForm = document.getElementById("errorForm");
const errorSuspicious = document.getElementById("errorSuspicious");
const errorType = document.getElementById("errorType");
const errorMeta = document.getElementById("errorMeta");

async function loadErrorLevel(level) {
    const response = await fetch(`/api/modules/error/item?level=${level}`);
    const data = await response.json();
    const item = data.item;
    errorTask.dataset.level = item.level;
    errorQuestion.textContent = item.question;
    errorAiAnswer.textContent = item.ai_answer;
    errorSuspicious.value = "";
    document.getElementById("errorExplanation").value = "";
    document.getElementById("errorEvidence").value = "";
    document.getElementById("errorRewrite").value = "";
    errorMeta.textContent = "";
}

levelButtons.forEach((button) => {
    button.addEventListener("click", () => {
        levelButtons.forEach((item) => item.classList.toggle("active", item === button));
        loadErrorLevel(button.dataset.errorLevel);
    });
});

if (errorAiAnswer) {
    errorAiAnswer.addEventListener("mouseup", () => {
        const selected = window.getSelection().toString().trim();
        if (selected) {
            errorSuspicious.value = selected;
        }
    });
}

if (errorForm) {
    errorForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const response = await fetch("/api/modules/error/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                level: errorTask.dataset.level,
                suspicious_text: errorSuspicious.value,
                error_type: errorType.value,
                explanation: document.getElementById("errorExplanation").value,
                evidence: document.getElementById("errorEvidence").value,
                rewrite: document.getElementById("errorRewrite").value,
            }),
        });
        const data = await response.json();
        errorMeta.textContent = `${data.score}/100 · Lỗi chuẩn: ${data.expected.error_type}`;
        if (data.score < 70) {
            document.getElementById("errorRewrite").value += `\n\nGợi ý sửa: ${data.expected.corrected_answer}`;
        }
    });
}

const detectiveTask = document.getElementById("detectiveTask");
const detectiveText = document.getElementById("detectiveText");
const detectiveTaskLabel = document.getElementById("detectiveTaskLabel");
const detectiveTaskTitle = document.getElementById("detectiveTaskTitle");
const detectiveForm = document.getElementById("detectiveForm");
const detectiveMeta = document.getElementById("detectiveMeta");
const detectiveSuspicious = document.getElementById("detectiveSuspicious");
const detectiveNodes = document.querySelectorAll("[data-station-code]");

async function loadDetectiveStation(code) {
    const response = await fetch(`/api/modules/detective/station?code=${code}`);
    const data = await response.json();
    const station = data.station;
    detectiveTask.dataset.code = station.code;
    detectiveTaskLabel.textContent = `${station.code} · ${station.title}`;
    detectiveTaskTitle.textContent = station.task;
    detectiveText.textContent = station.text;
    detectiveSuspicious.value = "";
    document.getElementById("detectiveExplanation").value = "";
    document.getElementById("detectiveEvidence").value = "";
    document.getElementById("detectiveRewrite").value = "";
    detectiveMeta.textContent = "";
    detectiveNodes.forEach((node) => node.classList.toggle("current", node.dataset.stationCode === station.code));
}

detectiveNodes.forEach((node) => {
    node.addEventListener("click", () => loadDetectiveStation(node.dataset.stationCode));
});

if (detectiveText) {
    detectiveText.addEventListener("mouseup", () => {
        const selected = window.getSelection().toString().trim();
        if (selected) {
            detectiveSuspicious.value = selected;
        }
    });
}

if (detectiveForm) {
    detectiveForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const response = await fetch("/api/modules/detective/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                code: detectiveTask.dataset.code,
                suspicious_text: detectiveSuspicious.value,
                error_type: document.getElementById("detectiveType").value,
                explanation: document.getElementById("detectiveExplanation").value,
                evidence: document.getElementById("detectiveEvidence").value,
                rewrite: document.getElementById("detectiveRewrite").value,
            }),
        });
        const data = await response.json();
        detectiveMeta.textContent = `${data.score}/100 · Lỗi chuẩn: ${data.expected.error_type}`;
        if (data.passed) {
            const current = [...detectiveNodes].find((node) => node.dataset.stationCode === detectiveTask.dataset.code);
            const next = current?.nextElementSibling;
            current.classList.add("completed");
            current.innerHTML = `<span>${current.dataset.stationCode}</span><small>${current.querySelector("small")?.textContent || "Hoàn thành"}</small>`;
            if (window.lucide) {
                const icon = document.createElement("i");
                icon.setAttribute("data-lucide", "check");
                current.appendChild(icon);
                window.lucide.createIcons();
            }
            if (next) {
                next.disabled = false;
                next.classList.add("active");
                next.querySelector("i")?.setAttribute("data-lucide", "car");
                if (window.lucide) {
                    window.lucide.createIcons();
                }
            }
        } else {
            document.getElementById("detectiveRewrite").value += `\n\nGợi ý sửa: ${data.expected.rewrite}`;
        }
    });
}

const argumentPieces = document.querySelectorAll(".argument-piece");
const bucketDropzones = document.querySelectorAll(".bucket-dropzone");
const scoreArgumentMap = document.getElementById("scoreArgumentMap");
const argumentResult = document.getElementById("argumentResult");
const retryArgumentMap = document.getElementById("retryArgumentMap");

argumentPieces.forEach((piece) => {
    piece.addEventListener("dragstart", () => {
        piece.classList.add("is-dragging");
    });
    piece.addEventListener("dragend", () => {
        piece.classList.remove("is-dragging");
    });
});

bucketDropzones.forEach((zone) => {
    zone.addEventListener("dragover", (event) => {
        event.preventDefault();
        zone.closest(".argument-bucket").classList.add("is-over");
    });
    zone.addEventListener("dragleave", () => {
        zone.closest(".argument-bucket").classList.remove("is-over");
    });
    zone.addEventListener("drop", (event) => {
        event.preventDefault();
        const dragging = document.querySelector(".argument-piece.is-dragging");
        if (dragging) {
            zone.appendChild(dragging);
        }
        zone.closest(".argument-bucket").classList.remove("is-over");
    });
});

if (scoreArgumentMap) {
    scoreArgumentMap.addEventListener("click", async () => {
        const placements = {};
        document.querySelectorAll(".argument-bucket").forEach((bucket) => {
            const bucketKey = bucket.dataset.bucketKey;
            bucket.querySelectorAll(".argument-piece").forEach((piece) => {
                placements[piece.dataset.pieceId] = bucketKey;
            });
        });
        const response = await fetch("/api/modules/argument-map/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ placements }),
        });
        const data = await response.json();
        const passed = data.score >= 80;
        argumentResult.hidden = false;
        document.getElementById("argumentScore").textContent = `${data.score}/100`;
        document.getElementById("argumentResultTitle").textContent = passed ? "Đạt yêu cầu" : "Cần chỉnh lại bản đồ";
        document.getElementById("argumentResultBadge").textContent = passed ? "Hoàn thành" : "Chưa đạt";
        document.getElementById("argumentFeedback").textContent = passed
            ? `${data.correct}/${data.total} mảnh đúng. Bạn có thể chuyển sang bài tiếp theo.`
            : `${data.correct}/${data.total} mảnh đúng. Sửa các thẻ màu đỏ rồi chấm lại.`;
        argumentResult.classList.toggle("is-passed", passed);
        argumentResult.classList.toggle("needs-retry", !passed);
        data.details.forEach((detail) => {
            const piece = document.querySelector(`[data-piece-id="${detail.piece_id}"]`);
            if (piece) {
                piece.classList.toggle("correct", detail.correct);
                piece.classList.toggle("wrong", !detail.correct);
            }
        });
        if (window.lucide) {
            window.lucide.createIcons();
        }
        argumentResult.scrollIntoView({ behavior: "smooth", block: "center" });
    });
}

if (retryArgumentMap) {
    retryArgumentMap.addEventListener("click", () => {
        argumentPieces.forEach((piece) => {
            piece.classList.remove("correct", "wrong");
            document.getElementById("argumentPieces")?.appendChild(piece);
        });
        argumentResult.hidden = true;
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

const modeButtons = document.querySelectorAll("[data-debate-mode]");
const findDebateMatch = document.getElementById("findDebateMatch");
const matchStatus = document.getElementById("matchStatus");
const battleStatus = document.getElementById("battleStatus");
const debateArena = document.getElementById("debateArena");
const debateTopic = document.getElementById("debateTopic");
const debateSideA = document.getElementById("debateSideA");
const debateSideB = document.getElementById("debateSideB");
const debateTimer = document.getElementById("debateTimer");
const playerArgument = document.getElementById("playerArgument");
const finishDebateTurn = document.getElementById("finishDebateTurn");
const opponentTranscript = document.getElementById("opponentTranscript");
const debateResult = document.getElementById("debateResult");
const voiceArgumentButton = document.getElementById("voiceArgumentButton");
const voiceArgumentStatus = document.getElementById("voiceArgumentStatus");
const soloMatchOverlay = document.getElementById("soloMatchOverlay");
const soloVsScreen = document.getElementById("soloVsScreen");
const matchCountdown = document.getElementById("matchCountdown");
const matchmakingTitle = document.getElementById("matchmakingTitle");
const matchmakingHint = document.getElementById("matchmakingHint");
const readyDebateMatch = document.getElementById("readyDebateMatch");
const cancelDebateMatch = document.getElementById("cancelDebateMatch");
const cancelDebateMatchSecondary = document.getElementById("cancelDebateMatchSecondary");

const debateState = {
    mode: "solo",
    topicIndex: 0,
    timer: null,
    matchTimer: null,
    matchSeconds: 23,
    seconds: 30,
};

function setDebateStatus(message) {
    if (matchStatus) {
        matchStatus.textContent = message;
    }
    if (battleStatus) {
        battleStatus.textContent = message;
    }
}

modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
        debateState.mode = button.dataset.debateMode;
        modeButtons.forEach((item) => item.classList.toggle("active", item === button));
        setDebateStatus(debateState.mode === "solo" ? "Solo Rank: ghép với AI Challenger cùng cấp." : "Phòng 5 người: tìm đủ 5 slot, thiếu người sẽ lấp AI bot.");
    });
});

async function loadDebateTopic(index) {
    const response = await fetch(`/api/modules/debate/topic?index=${index}`);
    const data = await response.json();
    debateState.topicIndex = index % data.total;
    debateArena.dataset.topicIndex = debateState.topicIndex;
    debateTopic.textContent = data.topic.title;
    debateSideA.textContent = data.topic.side_a;
    debateSideB.textContent = data.topic.side_b;
}

function startDebateTimer() {
    clearInterval(debateState.timer);
    debateState.seconds = 30;
    debateTimer.textContent = `${debateState.seconds}s`;
    debateState.timer = setInterval(() => {
        debateState.seconds -= 1;
        debateTimer.textContent = `${debateState.seconds}s`;
        if (debateState.seconds <= 0) {
            clearInterval(debateState.timer);
            finishDebateTurn.click();
        }
    }, 1000);
}

function closeSoloMatchOverlay() {
    clearInterval(debateState.matchTimer);
    if (soloMatchOverlay) {
        soloMatchOverlay.hidden = true;
    }
    if (findDebateMatch) {
        findDebateMatch.disabled = false;
    }
}

function openSoloMatchOverlay() {
    if (!soloMatchOverlay || !matchCountdown) {
        return;
    }

    debateState.matchSeconds = 23;
    matchCountdown.textContent = debateState.matchSeconds;
    matchmakingTitle.textContent = "Đang ghép đối thủ";
    matchmakingHint.textContent = "Hệ thống đang tìm AI đối thủ cùng cấp lập luận.";
    soloMatchOverlay.hidden = false;
    clearInterval(debateState.matchTimer);
    debateState.matchTimer = setInterval(() => {
        debateState.matchSeconds -= 1;
        matchCountdown.textContent = debateState.matchSeconds;
        if (debateState.matchSeconds <= 18) {
            matchmakingTitle.textContent = "Đã tìm thấy đối thủ";
            matchmakingHint.textContent = "Bấm Sẵn sàng để vào màn VS.";
        }
        if (debateState.matchSeconds <= 0) {
            closeSoloMatchOverlay();
            setDebateStatus("Đã hủy ghép trận do quá thời gian sẵn sàng.");
        }
    }, 1000);
}

async function enterSoloRankMatch() {
    closeSoloMatchOverlay();
    setDebateStatus("Đã xác nhận. Chuẩn bị vào VS...");
    await loadDebateTopic((debateState.topicIndex + 1) % 3);
    debateArena.hidden = true;
    debateResult.hidden = true;
    if (soloVsScreen) {
        soloVsScreen.hidden = false;
    }
    await new Promise((resolve) => setTimeout(resolve, 1200));
    if (soloVsScreen) {
        soloVsScreen.hidden = true;
    }
    debateArena.hidden = false;
    playerArgument.value = "";
    opponentTranscript.textContent = "";
    setDebateStatus("Trận Solo Rank bắt đầu.");
    playerArgument.focus();
    startDebateTimer();
}

if (findDebateMatch) {
    findDebateMatch.addEventListener("click", async () => {
        if (debateState.mode !== "solo") {
            if (findDebateMatch.dataset.roomUrl) {
                window.location.href = findDebateMatch.dataset.roomUrl;
                return;
            }
            setDebateStatus("Phòng 5 người đang mở hàng chờ.");
            return;
        }

        if (findDebateMatch.dataset.matchingUrl) {
            window.location.href = findDebateMatch.dataset.matchingUrl;
            return;
        }

        setDebateStatus("Đang mở hàng chờ Solo Rank...");
        findDebateMatch.disabled = true;
        openSoloMatchOverlay();
    });
}

const roomCountdown = document.getElementById("roomCountdown");
const roomTitle = document.getElementById("roomTitle");
const roomStatus = document.getElementById("roomStatus");
const roomReadyButton = document.getElementById("roomReadyButton");
const roomSlots = document.querySelectorAll("[data-room-slot]");
if (roomCountdown && roomSlots.length) {
    let seconds = Number(roomCountdown.textContent || "18");
    let filled = 1;
    const roomNames = ["AI Minh", "AI Trâm", "AI Quân", "AI Lan"];

    function markRoomReady() {
        roomSlots.forEach((slot, index) => {
            slot.classList.add("filled", "ready");
            if (index > 0 && slot.querySelector("small")) {
                slot.querySelector("small").textContent = "Sẵn sàng";
            }
            const icon = slot.querySelector("[data-lucide]");
            if (icon) {
                icon.setAttribute("data-lucide", index === 0 ? "user-check" : "bot");
            }
        });
        roomCountdown.textContent = "5/5";
        if (roomTitle) {
            roomTitle.textContent = "Phòng đã đủ người";
        }
        if (roomStatus) {
            roomStatus.textContent = "Tất cả đã sẵn sàng. Bấm Sẵn sàng để vào trận.";
        }
        if (roomReadyButton) {
            roomReadyButton.disabled = false;
        }
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    const roomTimer = setInterval(() => {
        seconds -= 1;
        roomCountdown.textContent = seconds;

        if (filled < roomSlots.length && (seconds === 15 || seconds === 12 || seconds === 9 || seconds === 6)) {
            const slot = roomSlots[filled];
            slot.classList.add("filled");
            slot.querySelector("strong").textContent = roomNames[filled - 1] || `AI ${filled}`;
            slot.querySelector("small").textContent = "Đã vào phòng";
            const icon = slot.querySelector("[data-lucide]");
            if (icon) {
                icon.setAttribute("data-lucide", "bot");
            }
            filled += 1;
            if (roomStatus) {
                roomStatus.textContent = `Đã có ${filled}/5 người trong phòng.`;
            }
            if (window.lucide) {
                window.lucide.createIcons();
            }
        }

        if (filled >= roomSlots.length || seconds <= 0) {
            clearInterval(roomTimer);
            markRoomReady();
        }
    }, 1000);

    if (roomReadyButton) {
        roomReadyButton.addEventListener("click", () => {
            if (roomReadyButton.disabled) {
                return;
            }
            window.location.href = roomReadyButton.dataset.roomBattleUrl || "/app/modules/dau-truong-lap-luan/battle?topic=0";
        });
    }
}

const roomDebateForm = document.getElementById("roomDebateForm");
const roomDebateInput = document.getElementById("roomDebateInput");
const roomTranscript = document.getElementById("roomTranscript");
const roomPhaseLabel = document.getElementById("roomPhaseLabel");
const roomTurnSpeaker = document.getElementById("roomTurnSpeaker");
const roomTurnRole = document.getElementById("roomTurnRole");
const roomBattleStatus = document.getElementById("roomBattleStatus");
const roomPlayerCards = document.querySelectorAll("[data-room-player]");
if (roomDebateForm && roomDebateInput && roomTranscript) {
    const roomTurns = [
        { name: "Bạn", role: "Mở luận điểm cho đội Ủng hộ", phase: "Vòng 1 · Mở luận điểm", prompt: "Hãy nêu quan điểm chính và lý do đầu tiên." },
        { name: "AI Minh", role: "Bổ sung bằng chứng", phase: "Vòng 2 · Bằng chứng", prompt: "AI Minh đang bổ sung ví dụ và dữ liệu." },
        { name: "AI Trâm", role: "Phản biện từ đội Phản đối", phase: "Vòng 3 · Phản biện chéo", prompt: "AI Trâm đang nêu điểm yếu trong lập luận." },
        { name: "AI Quân", role: "Bắt lỗi ngụy biện", phase: "Vòng 3 · Bắt lỗi", prompt: "AI Quân đang kiểm tra giả định và lỗi suy luận." },
        { name: "AI Lan", role: "Tổng kết viên", phase: "Vòng 4 · Tổng kết", prompt: "AI Lan đang tổng kết điểm mạnh/yếu của hai đội." },
    ];
    let roomTurnIndex = 0;

    function setRoomTurn(index) {
        roomTurnIndex = index % roomTurns.length;
        const turn = roomTurns[roomTurnIndex];
        if (roomPhaseLabel) {
            roomPhaseLabel.textContent = turn.phase;
        }
        if (roomTurnSpeaker) {
            roomTurnSpeaker.textContent = `Lượt của ${turn.name}`;
        }
        if (roomTurnRole) {
            roomTurnRole.textContent = turn.role;
        }
        roomPlayerCards.forEach((card) => {
            card.classList.toggle("active", Number(card.dataset.roomPlayer) === roomTurnIndex);
        });
        roomDebateInput.disabled = roomTurnIndex !== 0;
        roomDebateForm.querySelector("button").disabled = roomTurnIndex !== 0;
        roomDebateInput.placeholder = roomTurnIndex === 0 ? turn.prompt : "Đang chờ người chơi khác phát biểu...";
    }

    function addRoomTranscript(name, text, type = "") {
        const item = document.createElement("article");
        item.className = type;
        item.innerHTML = `<strong>${name}</strong><p>${text}</p>`;
        roomTranscript.appendChild(item);
        roomTranscript.scrollTop = roomTranscript.scrollHeight;
    }

    function playAiRoomTurns() {
        if (roomTurnIndex === 0) {
            return;
        }
        const turn = roomTurns[roomTurnIndex];
        if (roomBattleStatus) {
            roomBattleStatus.textContent = `${turn.name} đang phát biểu...`;
        }
        setTimeout(() => {
            addRoomTranscript(turn.name, turn.prompt, "ai");
            if (roomTurnIndex >= roomTurns.length - 1) {
                setRoomTurn(0);
                if (roomBattleStatus) {
                    roomBattleStatus.textContent = "Một vòng tranh luận đã xong. Bạn có thể mở lượt tiếp theo.";
                }
                return;
            }
            setRoomTurn(roomTurnIndex + 1);
            playAiRoomTurns();
        }, 850);
    }

    roomDebateForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = roomDebateInput.value.trim();
        if (text.length < 12) {
            if (roomBattleStatus) {
                roomBattleStatus.textContent = "Phần phát biểu cần rõ hơn một chút.";
            }
            return;
        }
        addRoomTranscript("Bạn", text, "self");
        roomDebateInput.value = "";
        setRoomTurn(1);
        playAiRoomTurns();
    });

    setRoomTurn(0);
}

[cancelDebateMatch, cancelDebateMatchSecondary].forEach((button) => {
    if (!button) {
        return;
    }

    button.addEventListener("click", () => {
        closeSoloMatchOverlay();
        setDebateStatus("Đã hủy ghép trận.");
    });
});

if (readyDebateMatch) {
    readyDebateMatch.addEventListener("click", (event) => {
        if (readyDebateMatch.dataset.vsUrl) {
            event.preventDefault();
            window.location.href = readyDebateMatch.dataset.vsUrl;
            return;
        }
        enterSoloRankMatch();
    });
}

if (matchCountdown && !soloMatchOverlay) {
    debateState.matchSeconds = Number(matchCountdown.textContent || "23");
    clearInterval(debateState.matchTimer);
    debateState.matchTimer = setInterval(() => {
        debateState.matchSeconds -= 1;
        matchCountdown.textContent = debateState.matchSeconds;
        if (matchmakingTitle && matchmakingHint && debateState.matchSeconds <= 18) {
            matchmakingTitle.textContent = "Đã tìm thấy đối thủ";
            matchmakingHint.textContent = "Bấm Sẵn sàng để vào màn VS.";
        }
        if (debateState.matchSeconds <= 0) {
            clearInterval(debateState.matchTimer);
            window.location.href = "/app/modules/dau-truong-lap-luan";
        }
    }, 1000);
}

const vsCountdown = document.getElementById("vsCountdown");
if (soloVsScreen && soloVsScreen.dataset.battleUrl && vsCountdown) {
    let seconds = Number(vsCountdown.textContent || "3");
    const vsTimer = setInterval(() => {
        seconds -= 1;
        if (seconds <= 0) {
            clearInterval(vsTimer);
            window.location.href = soloVsScreen.dataset.battleUrl;
            return;
        }
        vsCountdown.textContent = seconds;
    }, 850);
}

if (debateArena && playerArgument && !debateArena.hidden) {
    playerArgument.focus();
    startDebateTimer();
}

if (voiceArgumentButton && playerArgument) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    function setVoiceState(listening, message) {
        isListening = listening;
        voiceArgumentButton.classList.toggle("is-listening", listening);
        voiceArgumentButton.setAttribute("aria-pressed", listening ? "true" : "false");
        voiceArgumentButton.innerHTML = `<i data-lucide="${listening ? "mic-off" : "mic"}"></i><span>${listening ? "Dừng nói" : "Nói lập luận"}</span>`;
        if (voiceArgumentStatus) {
            voiceArgumentStatus.textContent = message;
        }
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    function appendVoiceText(text) {
        const cleanText = String(text || "").trim();
        if (!cleanText) {
            return;
        }
        const current = playerArgument.value.trim();
        playerArgument.value = current ? `${current} ${cleanText}` : cleanText;
        playerArgument.focus();
        playerArgument.selectionStart = playerArgument.value.length;
        playerArgument.selectionEnd = playerArgument.value.length;
    }

    if (!SpeechRecognition) {
        voiceArgumentButton.disabled = true;
        if (voiceArgumentStatus) {
            voiceArgumentStatus.textContent = "Trình duyệt chưa hỗ trợ mic chuyển giọng nói.";
        }
    } else {
        recognition = new SpeechRecognition();
        recognition.lang = "vi-VN";
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.addEventListener("start", () => {
            setVoiceState(true, "Đang nghe tiếng Việt...");
            setDebateStatus("Mic đang nghe. Nói xong có thể sửa lại trước khi tung đòn.");
        });

        recognition.addEventListener("result", (event) => {
            let finalTranscript = "";
            let interimTranscript = "";
            for (let index = event.resultIndex; index < event.results.length; index += 1) {
                const transcript = event.results[index][0]?.transcript || "";
                if (event.results[index].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                appendVoiceText(finalTranscript);
            }
            if (voiceArgumentStatus) {
                voiceArgumentStatus.textContent = interimTranscript ? `Đang nghe: ${interimTranscript.trim()}` : "Đang nghe tiếng Việt...";
            }
        });

        recognition.addEventListener("end", () => {
            setVoiceState(false, "Mic tiếng Việt");
        });

        recognition.addEventListener("error", (event) => {
            const messages = {
                "not-allowed": "Bạn cần cấp quyền micro cho trình duyệt.",
                "no-speech": "Chưa nghe thấy giọng nói.",
                "audio-capture": "Không tìm thấy micro.",
                network: "Không kết nối được dịch vụ nhận giọng nói.",
            };
            setVoiceState(false, messages[event.error] || "Không nhận được giọng nói.");
            setDebateStatus(messages[event.error] || "Không nhận được giọng nói.");
        });

        voiceArgumentButton.addEventListener("click", () => {
            if (isListening) {
                recognition.stop();
                return;
            }
            try {
                recognition.start();
            } catch (error) {
                setVoiceState(false, "Mic đang khởi động, thử lại sau một chút.");
            }
        });
    }
}

if (finishDebateTurn) {
    finishDebateTurn.addEventListener("click", async () => {
        clearInterval(debateState.timer);
        const argument = playerArgument.value.trim();
        if (argument.length < 20) {
            setDebateStatus("Lập luận cần dài hơn một chút trước khi chấm.");
            startDebateTimer();
            return;
        }

        finishDebateTurn.disabled = true;
        setDebateStatus("AI trọng tài đang chấm...");
        const response = await fetch("/api/modules/debate/judge", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mode: debateState.mode,
                topic_index: debateArena.dataset.topicIndex,
                player_argument: argument,
            }),
        });
        const data = await response.json();
        finishDebateTurn.disabled = false;

        if (!response.ok) {
            setDebateStatus(data.error || "Không chấm được trận.");
            return;
        }

        if (data.result_url) {
            window.location.href = data.result_url;
            return;
        }

        opponentTranscript.textContent = data.opponent_argument;
        debateResult.hidden = false;
        const winnerText = {
            player: "Bạn thắng",
            opponent: "Đối thủ thắng",
            draw: "Hòa",
        }[data.winner];
        document.getElementById("debateWinner").textContent = winnerText;
        document.getElementById("debateScoreMeta").textContent = `Bạn ${data.player.total} · Đối thủ ${data.opponent.total} · ${data.rank_delta >= 0 ? "+" : ""}${data.rank_delta} rank`;
        document.getElementById("debateFeedback").textContent = data.feedback;
        if (document.getElementById("rankPoints")) {
            document.getElementById("rankPoints").textContent = data.rank_points;
        }
        if (document.getElementById("leaderboardSelf")) {
            document.getElementById("leaderboardSelf").textContent = data.rank_points;
        }
        const playerRubric = data.rubric_scores || data.player?.rubric_scores || [];
        const rubric = playerRubric.map((item) => [
            item.label,
            `${item.score}/${item.max}`,
        ]);
        document.getElementById("debateRubric").innerHTML = rubric
            .map(([label, value]) => `<article class="rubric-item"><span>${label}</span><strong>${value}</strong></article>`)
            .join("");
        setDebateStatus("Trận đấu đã kết thúc.");
    });
}

const promptCriticForm = document.getElementById("promptCriticForm");
if (promptCriticForm) {
    promptCriticForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const prompt = document.getElementById("criticPrompt").value.trim();
        const meta = document.getElementById("promptScoreMeta");
        if (prompt.length < 12) {
            meta.textContent = "Prompt cần dài hơn.";
            return;
        }
        const response = await fetch("/api/modules/prompt/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
        });
        const data = await response.json();
        if (!response.ok) {
            meta.textContent = data.error || "Không chấm được prompt.";
            return;
        }
        meta.textContent = data.feedback || "AI đã nhận xét. Giáo viên chấm cuối cùng.";
        const promptRubric = document.getElementById("promptRubric");
        if (promptRubric) {
            promptRubric.hidden = false;
        }
        data.rubric.forEach((item) => {
            const row = document.querySelector(`[data-rubric-key="${item.key}"]`);
            if (!row) {
                return;
            }
            row.querySelector("span").textContent = item.score >= 14 ? "Đã có" : "Cần bổ sung";
            row.querySelector("p").textContent = item.hint;
        });
        const suggestion = document.getElementById("promptSuggestion");
        suggestion.hidden = false;
        suggestion.textContent = data.suggestion;
    });
}

const profileRadar = document.getElementById("profileRadar");
if (profileRadar) {
    const scores = profileRadar.dataset.scores.split(",").map(Number);
    const svg = profileRadar.querySelector("svg");
    const center = 160;
    const maxRadius = 118;
    const labels = ["PT", "BC", "SL", "KN", "LL", "ĐL", "PĐ", "TĐ"];
    const radarColors = {
        ring: "rgba(180,122,22,.28)",
        axis: "rgba(180,122,22,.22)",
        label: "#8a5b16",
        fill: "rgba(207,61,50,.16)",
        stroke: "#cf3d32",
    };

    function point(index, value) {
        const angle = -Math.PI / 2 + (Math.PI * 2 * index) / scores.length;
        const radius = maxRadius * value;
        return [center + Math.cos(angle) * radius, center + Math.sin(angle) * radius];
    }

    const rings = [0.25, 0.5, 0.75, 1].map((scale) => {
        const points = scores.map((_, index) => point(index, scale).join(",")).join(" ");
        return `<polygon points="${points}" fill="none" stroke="${radarColors.ring}" stroke-width="1" />`;
    }).join("");

    const axes = scores.map((_, index) => {
        const [x, y] = point(index, 1);
        const [lx, ly] = point(index, 1.14);
        return `<line x1="${center}" y1="${center}" x2="${x}" y2="${y}" stroke="${radarColors.axis}" /><text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" font-size="12" font-weight="800" fill="${radarColors.label}">${labels[index]}</text>`;
    }).join("");

    const polygon = scores.map((score, index) => point(index, score / 100).join(",")).join(" ");
    svg.innerHTML = `${rings}${axes}<polygon points="${polygon}" fill="${radarColors.fill}" stroke="${radarColors.stroke}" stroke-width="3" /><circle cx="${center}" cy="${center}" r="3" fill="${radarColors.stroke}" />`;
}

const profileLine = document.getElementById("profileLine");
if (profileLine) {
    const values = profileLine.dataset.values.split(",").map(Number);
    profileLine.innerHTML = values
        .map((value) => `<span style="height: ${value}%;" title="${value}%"></span>`)
        .join("");
}

document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
        const input = document.getElementById(button.dataset.passwordToggle);
        if (!input) {
            return;
        }
        const isHidden = input.type === "password";
        input.type = isHidden ? "text" : "password";
        button.setAttribute("aria-label", isHidden ? "Ẩn mật khẩu" : "Hiện mật khẩu");
        button.innerHTML = `<i data-lucide="${isHidden ? "eye-off" : "eye"}"></i>`;
        if (window.lucide) {
            window.lucide.createIcons();
        }
    });
});

const avatarInput = document.querySelector("[data-avatar-input]");
const avatarPreview = document.querySelector("[data-avatar-preview]");
if (avatarInput && avatarPreview) {
    avatarInput.addEventListener("change", () => {
        const [file] = avatarInput.files;
        if (!file || !file.type.startsWith("image/")) {
            return;
        }
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            avatarPreview.innerHTML = `<img src="${reader.result}" alt="Avatar xem trước">`;
        });
        reader.readAsDataURL(file);
    });
}
