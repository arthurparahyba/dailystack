/**
 * Data models for DailyStack frontend
 */

export class Scenario {
    constructor({ title, description }) {
        this.title = title || '';
        this.description = description || '';
    }

    static fromDict(data) {
        if (!data) return null;
        return new Scenario(data);
    }
}

export class Flashcard {
    constructor({ question, answer, category, detailed_explanation, code_example }) {
        this.question = question || '';
        this.answer = answer || '';
        this.category = category || 'General';
        this.detailedExplanation = detailed_explanation || '';
        this.codeExample = code_example || '';
    }

    static fromDict(data) {
        if (!data) return null;
        return new Flashcard(data);
    }
}
