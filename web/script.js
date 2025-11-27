const API_BASE = ''; // Relative path since we are serving from Flask

// DOM Elements
const scenarioTitle = document.getElementById('scenario-title');
const scenarioDesc = document.getElementById('scenario-desc');

const cardTitle = document.getElementById('card-title');
const cardQuestion = document.getElementById('card-question');
const cardAnswer = document.getElementById('card-answer');
const cardDescription = document.getElementById('card-description');
const cardVisual = document.getElementById('card-visual');
const cardCode = document.getElementById('card-code');

const answerSection = document.getElementById('answer-section');
const btnReveal = document.getElementById('btn-reveal');
const btnNext = document.getElementById('btn-next');

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
    const authenticated = await checkAuth();
    if (authenticated) {
        loadScenario();
    } else {
        showCredentialsModal();
    }
});

async function checkAuth() {
    try {
        const res = await fetch(`${API_BASE}/check-auth`);
        const data = await res.json();
        return data.authenticated;
    } catch (err) {
        console.error("Auth check failed", err);
        return false;
    }
}

function showCredentialsModal() {
    const modal = document.getElementById('credentials-modal');
    modal.classList.remove('hidden');

    const form = document.getElementById('credentials-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const clientId = document.getElementById('stk-client-id').value;
        const clientKey = document.getElementById('stk-client-key').value;
        const realm = document.getElementById('stk-realm').value;

        try {
            const res = await fetch(`${API_BASE}/save-credentials`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    stk_client_id: clientId,
                    stk_client_key: clientKey,
                    stk_realm: realm
                })
            });

            if (res.ok) {
                modal.classList.add('hidden');
                loadScenario();
                loadCurrentFlashcard();
            } else {
                alert("Failed to save credentials");
            }
        } catch (err) {
            console.error("Save credentials failed", err);
            alert("Error saving credentials");
        }
    });
}

// Fetch Scenario
async function loadScenario() {
    try {
        const res = await fetch(`${API_BASE}/scenario`);
        const data = await res.json();

        // Check if data is valid (not null/empty)
        if (data && (data.title || data.description)) {
            scenarioTitle.textContent = data.title;
            scenarioDesc.textContent = data.problem_description || data.description;
            if (data.architectural_overview) {
                document.getElementById('scenario-arch').textContent = "Architecture: " + data.architectural_overview;
            }
            // Once scenario is loaded, load the flashcards
            loadCurrentFlashcard();
        } else {
            // Retry if data is not yet available
            console.log("Scenario not ready, retrying...");
            setTimeout(loadScenario, 1000);
        }
    } catch (err) {
        console.error("Failed to load scenario", err);
        // Retry on error
        setTimeout(loadScenario, 2000);
    }
}

// Fetch Current Flashcard
async function loadCurrentFlashcard() {
    try {
        const res = await fetch(`${API_BASE}/flashcard/current`);
        const data = await res.json();
        renderFlashcard(data);
    } catch (err) {
        console.error("Failed to load flashcard", err);
    }
}

// Load Chat History
async function loadChatHistory() {
    chatMessages.innerHTML = ''; // Clear existing messages
    try {
        const res = await fetch(`${API_BASE}/chat/history`);
        const messages = await res.json();
        messages.forEach(msg => {
            addMessage(msg.content, msg.role === 'bot' ? 'bot' : 'user');
        });
    } catch (err) {
        console.error("Failed to load chat history", err);
    }
}

// Render Flashcard
function renderFlashcard(data) {
    if (!data || !data.title) return;

    // Reset UI
    answerSection.classList.add('hidden');
    btnReveal.classList.remove('hidden');
    btnNext.classList.add('hidden');

    // Fill Content
    cardTitle.textContent = data.title;
    cardQuestion.textContent = data.question;

    // Hidden Content
    // Map new schema fields to existing UI
    cardAnswer.textContent = data.short_answer || data.answer;
    cardDescription.textContent = data.detailed_explanation || data.description;
    cardVisual.textContent = data.visual_example;
    cardCode.textContent = data.code_example;

    // Load chat history for this card
    loadChatHistory();
}

// Reveal Answer
btnReveal.addEventListener('click', () => {
    answerSection.classList.remove('hidden');
    btnReveal.classList.add('hidden');
    btnNext.classList.remove('hidden');
});

// Next Flashcard
btnNext.addEventListener('click', async () => {
    try {
        const res = await fetch(`${API_BASE}/flashcard/next`, { method: 'POST' });
        const data = await res.json();
        renderFlashcard(data);
    } catch (err) {
        console.error("Failed to load next flashcard", err);
    }
});

// Chat Logic
function addMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    chatInput.value = '';

    // Create a placeholder message for the bot response
    const botDiv = document.createElement('div');
    botDiv.classList.add('message', 'bot');
    const botP = document.createElement('p');
    botDiv.appendChild(botP);
    chatMessages.appendChild(botDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/ask-llm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        });

        if (!res.ok) {
            botP.textContent = "Sorry, I couldn't reach the server.";
            return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.substring(6);
                    if (dataStr.trim()) {
                        try {
                            const data = JSON.parse(dataStr);
                            if (data.answer) {
                                botP.textContent += data.answer;
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            } else if (data.error) {
                                botP.textContent = `Error: ${data.error}`;
                            }
                        } catch (e) {
                            console.error('Failed to parse SSE data:', e);
                        }
                    }
                }
            }
        }
    } catch (err) {
        console.error('Chat error:', err);
        botP.textContent = "Sorry, I couldn't reach the server.";
    }
}

btnSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
