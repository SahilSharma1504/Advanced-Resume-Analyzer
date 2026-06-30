const API_BASE_URL = "http://localhost:8081/api";

// Navigation Logic
function switchPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));

    document.getElementById(`page-${pageId}`).classList.add('active');

    let navItem = document.getElementById(`nav-${pageId}`);
    if (!navItem && pageId === 'dashboard') navItem = document.getElementById('nav-analyze');
    if (navItem) navItem.classList.add('active');
}

// Architecture Modal
function openArchModal() { document.getElementById('arch-modal').style.display = 'block'; }
document.getElementById('close-modal').addEventListener('click', () => { document.getElementById('arch-modal').style.display = 'none'; });
window.onclick = function (event) {
    const modal = document.getElementById('arch-modal');
    if (event.target == modal) { modal.style.display = "none"; }
}

// Global state
let analysisData = null;

// File Upload visual
const dropArea = document.getElementById('drop-area');
const resumeInput = document.getElementById('resume');
const fileNameDisplay = document.getElementById('file-name-display');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eName => {
    dropArea.addEventListener(eName, e => { e.preventDefault(); e.stopPropagation(); }, false);
});
['dragenter', 'dragover'].forEach(eName => {
    dropArea.addEventListener(eName, () => dropArea.classList.add('dragover'), false);
});
['dragleave', 'drop'].forEach(eName => {
    dropArea.addEventListener(eName, () => dropArea.classList.remove('dragover'), false);
});
dropArea.addEventListener('drop', e => {
    if (e.dataTransfer.files.length) {
        resumeInput.files = e.dataTransfer.files;
        updateFileName();
    }
});
resumeInput.addEventListener('change', updateFileName);

function updateFileName() {
    if (resumeInput.files.length) {
        fileNameDisplay.innerHTML = `<i class="fa-solid fa-file-check"></i> ${resumeInput.files[0].name}`;
    }
}

// Form Submission & Analysis
document.getElementById('analyze-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!resumeInput.files.length) return alert('Select a resume.');

    const analyzeBtn = document.getElementById('analyze-btn');
    const loader = document.getElementById('loader');

    analyzeBtn.style.display = 'none';
    loader.style.display = 'block';

    const formData = new FormData(e.target);

    try {
        const response = await fetch('http://localhost:8081/api/analyze-advanced', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Python AI service is not running. Please start the backend.");

        const data = await response.json();
        analysisData = data;

        // Save history in the background asynchronously
        const username = document.getElementById('username-input') ? document.getElementById('username-input').value.trim() : "";
        if (username) {
            fetch('http://localhost:8081/api/history/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    overall_score: data.overall_score || 0,
                    quality_score: data.quality_score || 0,
                    experience_score: data.experience_score || 0,
                    ats_score: data.ats_score || 0
                })
            }).catch(err => console.error("Could not save history background task.", err));
        }

        populateDashboard(data);
        switchPage('dashboard');

    } catch (err) {
        alert(err.message);
    } finally {
        analyzeBtn.style.display = 'block';
        loader.style.display = 'none';
    }
});

// Dashboard Rendering
function populateDashboard(data) {
    if (data.analysis_mode !== "LLM") {
        document.getElementById('llm-warning-banner').style.display = 'block';
    } else {
        document.getElementById('llm-warning-banner').style.display = 'none';
    }

    document.getElementById('domain-display').innerText = data.detected_domain || 'Unknown';
    document.getElementById('domain-conf').innerText = `(${data.domain_confidence}% Confidence)`;

    // Badges / Counters
    document.getElementById('word-count-badge').innerHTML = `<i class="fa-solid fa-file-word"></i> ${data.word_count || 0} Words`;

    // Rings
    renderRing('ring-final', data.overall_score || 0);
    renderRing('ring-quality', data.quality_score || 0);
    renderRing('ring-exp', data.experience_score || 0);
    renderRing('ring-ats', data.ats_score || 0);

    // Strengths and Weaknesses
    document.getElementById('strengths-list').innerHTML = (data.strengths || []).map(s => `<li>${s}</li>`).join('');
    document.getElementById('weakness-list').innerHTML = (data.weaknesses || []).map(s => `<li>${s}</li>`).join('');

    // Categorized Skills
    document.getElementById('tech-count').innerText = `(${data.technical_count || 0})`;
    document.getElementById('soft-count').innerText = `(${data.soft_count})`;
    document.getElementById('tools-count').innerText = `(${data.tools_count})`;

    const spellingBadge = document.getElementById('spelling-badge');
    if (spellingBadge) {
        if (data.spelling_mistakes > 0) {
            spellingBadge.style.display = 'inline-block';
            spellingBadge.innerText = `\u26A0\uFE0F ${data.spelling_mistakes} Typos`;
        } else {
            spellingBadge.style.display = 'none';
        }
    }

    const weakBadge = document.getElementById('weak-phrase-badge');
    if (weakBadge) {
        if (data.weak_phrases > 0) {
            weakBadge.style.display = 'inline-block';
            weakBadge.innerText = `\u26A0\uFE0F ${data.weak_phrases} Weak Phrases`;
        } else {
            weakBadge.style.display = 'none';
        }
    }


    if (data.raw_text) {
        document.getElementById('live-editor').value = data.raw_text;
    }

    document.getElementById('chips-tech').innerHTML = (data.technical_skills || []).map(s => `<span class="chip matched">${s}</span>`).join('') || '<i>None detected</i>';
    document.getElementById('chips-soft').innerHTML = (data.soft_skills || []).map(s => `<span class="chip matched" style="border-color:#10b981; color:#10b981;">${s}</span>`).join('') || '<i>None detected</i>';
    document.getElementById('chips-tools').innerHTML = (data.tools || []).map(s => `<span class="chip missing" style="border-color:#f59e0b; color:#f59e0b;">${s}</span>`).join('') || '<i>None detected</i>';
}

function renderRing(elementId, targetScore) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const parent = el.parentElement;
    let color = targetScore >= 80 ? 'var(--success)' : targetScore >= 50 ? 'var(--warning)' : 'var(--danger)';

    let current = 0;
    const interval = setInterval(() => {
        current++;
        el.innerText = current + '%';
        parent.style.background = `conic-gradient(${color} ${current * 3.6}deg, var(--glass-border) 0deg)`;
        if (current >= targetScore || targetScore === 0) {
            clearInterval(interval);
            el.innerText = targetScore + '%';
        }
    }, 15);
}

// ==========================================
// LIVE EDITOR LOGIC (DEBOUNCED)
// ==========================================
let typingTimer;
const doneTypingInterval = 1200; // Wait 1.2s after user stops typing
const liveEditor = document.getElementById('live-editor');
const liveIndicator = document.getElementById('live-saving-indicator');

if (liveEditor) {
    liveEditor.addEventListener('input', () => {
        clearTimeout(typingTimer);
        liveIndicator.style.display = 'block'; // Show scoring loader

        typingTimer = setTimeout(async () => {
            const rawText = liveEditor.value;
            if (!rawText.trim()) {
                liveIndicator.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/quick-score`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: rawText })
                });

                if (response.ok) {
                    const data = await response.json();
                    populateDashboard(data); // Re-render the rings and chips!
                }
            } catch (err) {
                console.error("Live Editor Sync Failed:", err);
            } finally {
                liveIndicator.style.display = 'none';
            }

        }, doneTypingInterval);
    });
}

// Chatbot functionality
function toggleChat() {
    const panel = document.getElementById('chat-panel');
    panel.style.display = panel.style.display === 'flex' ? 'none' : 'flex';
}

function handleChatEnter(e) {
    if (e.key === 'Enter') sendChat();
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    const chatBody = document.getElementById('chat-body');
    chatBody.innerHTML += `<div class="msg user">${msg}</div>`;
    input.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const res = await fetch('http://localhost:8081/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, context: analysisData || {} })
        });
        const data = await res.json();
        chatBody.innerHTML += `<div class="msg bot">${data.reply}</div>`;
    } catch (err) {
        chatBody.innerHTML += `<div class="msg bot text-danger">Server offline.</div>`;
    }
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Bullet Improver functionality
document.getElementById('btn-improve').addEventListener('click', async () => {
    const input = document.getElementById('bullet-input').value.trim();
    if (!input) return;

    document.getElementById('btn-improve').innerText = '...';

    try {
        const res = await fetch('http://localhost:8081/api/improve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bullet: input })
        });
        const data = await res.json();
        const out = document.getElementById('bullet-output');
        out.style.display = 'block';
        out.innerHTML = `<strong>✨ Improved:</strong><br>${data.improved_bullet}`;
    } catch (err) {
        alert("Bullet improver offline");
    } finally {
        document.getElementById('btn-improve').innerText = 'Improve';
    }
});

document.getElementById('export-pdf').addEventListener('click', () => {
    const element = document.getElementById('page-dashboard');
    const body = document.body;

    // Temporarily apply PDF mode overrides
    body.classList.add('pdf-mode');
    element.classList.add('pdf-mode');

    // Slight delay to allow CSS reflow
    setTimeout(() => {
        html2pdf().from(element).set({
            margin: 10,
            filename: 'Resume_Analysis.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
            jsPDF: { unit: 'mm', format: 'a3', orientation: 'portrait' }
        }).save().then(() => {
            // Revert changes
            body.classList.remove('pdf-mode');
            element.classList.remove('pdf-mode');
        });
    }, 100);
});

// ==========================================
// HISTORY & PROGRESS TRACKING LOCIG (SQLITE)
// ==========================================
let progressChartInstance = null;
const historyModal = document.getElementById('history-modal');
const closeHistoryModal = document.getElementById('close-history-modal');

closeHistoryModal.onclick = () => historyModal.style.display = 'none';

function openHistoryModal() {
    const username = document.getElementById('username-input') ? document.getElementById('username-input').value.trim() : "";
    if (!username) {
        alert("Please enter a username on the Evaluate page to view your history.");
        return;
    }

    historyModal.style.display = 'block';
    fetchAndRenderHistory(username);
}

async function fetchAndRenderHistory(username) {
    try {
        const res = await fetch(`http://localhost:8081/api/history/${username}`);
        const data = await res.json();

        if (!data || data.length === 0) {
            alert("No history found for this username yet. Run an evaluation first!");
            if (progressChartInstance) progressChartInstance.destroy();
            return;
        }

        const labels = data.map(record => new Date(record.timestamp).toLocaleDateString() + " " + new Date(record.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        const overallData = data.map(record => record.overallScore);
        const atsData = data.map(record => record.atsScore);

        const ctx = document.getElementById('progressChart').getContext('2d');

        if (progressChartInstance) {
            progressChartInstance.destroy();
        }

        progressChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Overall Score',
                        data: overallData,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.2)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'ATS Compatibility',
                        data: atsData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#9ca3af' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#9ca3af', maxRotation: 45, minRotation: 45 }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
    } catch (err) {
        console.error("Failed to load history chart:", err);
    }
}
