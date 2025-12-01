/**
 * API Client for DailyStack
 */

import { Scenario, Flashcard } from './models';

const API_BASE = '/api';

/**
 * Fetch the daily scenario
 * @returns {Promise<Scenario>} Scenario object
 */
export async function fetchScenario() {
    const res = await fetch(`${API_BASE}/scenario`);
    if (!res.ok) throw new Error('Failed to fetch scenario');
    const data = await res.json();
    return Scenario.fromDict(data);
}

/**
 * Fetch the current flashcard
 * @returns {Promise<Flashcard>} Flashcard object
 */
export async function fetchCurrentFlashcard() {
    const res = await fetch(`${API_BASE}/flashcard/current`);
    if (!res.ok) throw new Error('Failed to fetch flashcard');
    const data = await res.json();
    return Flashcard.fromDict(data);
}

/**
 * Fetch the next flashcard
 * @returns {Promise<Flashcard>} Flashcard object
 */
export async function fetchNextFlashcard() {
    const res = await fetch(`${API_BASE}/flashcard/next`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to fetch next flashcard');
    const data = await res.json();
    return Flashcard.fromDict(data);
}
