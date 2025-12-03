import { writable } from 'svelte/store';
import * as api from './api';

// Stores
export const scenario = writable(null);
export const flashcard = writable(null);
export const loading = writable(true);
export const error = writable(null);
export const showAnswer = writable(false);
export const hasStarted = writable(false);

// Actions
export function startChallenge() {
    hasStarted.set(true);
}
export async function loadDailyChallenge() {
    loading.set(true);
    error.set(null);

    // Poll for status
    const pollInterval = 1000; // 1 second
    const maxRetries = 60; // 1 minute timeout
    let retries = 0;

    const checkStatus = async () => {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) throw new Error('Failed to check status');
            return await res.json();
        } catch (e) {
            console.error("Status check failed:", e);
            return { loading: true, has_data: false };
        }
    };

    try {
        while (retries < maxRetries) {
            const status = await checkStatus();

            if (status.error) {
                throw new Error(status.error);
            }

            if (!status.loading && status.has_data) {
                // Data is ready, fetch it
                const [scenarioData, flashcardData] = await Promise.all([
                    api.fetchScenario(),
                    api.fetchCurrentFlashcard()
                ]);
                console.log(scenarioData);
                scenario.set(scenarioData);
                flashcard.set(flashcardData);
                return;
            }

            if (!status.loading && !status.has_data) {
                throw new Error("Backend finished loading but no data available");
            }

            // Still loading, wait and retry
            await new Promise(resolve => setTimeout(resolve, pollInterval));
            retries++;
        }
        throw new Error("Timeout waiting for backend data");
    } catch (e) {
        error.set(e.message);
    } finally {
        loading.set(false);
    }
}

// Track if we've already requested an explanation for the current card
let explanationRequested = false;

// Reset explanation flag when card changes
flashcard.subscribe(() => {
    explanationRequested = false;
});

export const messages = writable([]);
export const isGenerating = writable(false);

export function toggleAnswer() {
    showAnswer.update(n => {
        const newValue = !n;
        if (newValue && !explanationRequested) {
            triggerExplanation();
        }
        return newValue;
    });
}

async function triggerExplanation() {
    explanationRequested = true;
    isGenerating.set(true);

    // Get current state
    let currentScenario;
    let currentFlashcard;

    const unsubscribeScenario = scenario.subscribe(value => currentScenario = value);
    const unsubscribeFlashcard = flashcard.subscribe(value => currentFlashcard = value);

    unsubscribeScenario();
    unsubscribeFlashcard();

    if (!currentScenario || !currentFlashcard) {
        isGenerating.set(false);
        return;
    }

    const prompt = `Dada a pergunta e a resposta fornecida com o cenario correspondente na qual a pergunta faz parte, gere uma explicação o mais didática possível com exemplos de código.
Construa os exemplos em java e considere que a stack é Java com AWS além de docker e terraform.

Titulo: ${currentScenario.title}
Contexto: ${currentScenario.description}
Pergunta: ${currentFlashcard.question}
Resposta: ${currentFlashcard.answer}`;

    try {
        const res = await api.askLlm(prompt, true); // hidden=true
        if (!res.ok) throw new Error("Failed to fetch explanation");

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let botMessage = { role: 'bot', content: '' };

        // Add empty bot message to start
        messages.update(msgs => [...msgs, botMessage]);

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.answer) {
                            botMessage.content += data.answer;
                            // Update the last message
                            messages.update(msgs => {
                                const newMsgs = [...msgs];
                                newMsgs[newMsgs.length - 1] = { ...botMessage };
                                return newMsgs;
                            });
                        }
                    } catch (e) {
                        console.error("Error parsing SSE data", e);
                    }
                }
            }
        }
    } catch (e) {
        console.error("Error fetching explanation:", e);
        messages.update(msgs => [...msgs, { role: 'bot', content: "Sorry, I couldn't generate an explanation at this time." }]);
    } finally {
        isGenerating.set(false);
    }
}

export async function nextCard() {
    loading.set(true); // Optional: show loading between cards?
    showAnswer.set(false);
    try {
        const nextCardData = await api.fetchNextFlashcard();
        flashcard.set(nextCardData);
    } catch (e) {
        error.set(e.message);
    } finally {
        loading.set(false);
    }
}
