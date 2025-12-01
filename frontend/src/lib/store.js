import { writable } from 'svelte/store';
import * as api from './api';

// Stores
export const scenario = writable(null);
export const flashcard = writable(null);
export const loading = writable(true);
export const error = writable(null);
export const showAnswer = writable(false);

// Actions
export async function loadDailyChallenge() {
    loading.set(true);
    error.set(null);
    try {
        const [scenarioData, flashcardData] = await Promise.all([
            api.fetchScenario(),
            api.fetchCurrentFlashcard()
        ]);
        console.log(scenarioData);
        scenario.set(scenarioData);
        flashcard.set(flashcardData);
    } catch (e) {
        error.set(e.message);
    } finally {
        loading.set(false);
    }
}

export function toggleAnswer() {
    showAnswer.update(n => !n);
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
