<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { Flashcard } from "../models";
    export let flashcard: Flashcard | null = null;
    export let showAnswer = false;

    const dispatch = createEventDispatcher();

    function handleClick() {
        dispatch("toggle");
    }

    function handleKeydown(e) {
        if (e.key === "Enter") {
            dispatch("toggle");
        }
    }
</script>

<div class="card-container">
    <div
        class="card"
        class:flipped={showAnswer}
        on:click={handleClick}
        on:keydown={handleKeydown}
        role="button"
        tabindex="0"
    >
        <div class="card-front">
            <span class="category">{flashcard.category || "General"}</span>
            <h2>{flashcard.question}</h2>
            <p class="hint">Click to reveal answer</p>
        </div>
        <div class="card-back">
            <h3>Answer</h3>
            <p>{flashcard.answer}</p>
            {#if flashcard.detailedExplanation}
                <div class="explanation">
                    <h4>Detailed Explanation</h4>
                    <p>{flashcard.detailedExplanation}</p>
                </div>
            {/if}
            {#if flashcard.codeExample}
                <pre><code>{flashcard.codeExample}</code></pre>
            {/if}
        </div>
    </div>
</div>

<style>
    .card-container {
        perspective: 1000px;
        margin-bottom: 2rem;
    }

    .card {
        position: relative;
        width: 100%;
        min-height: 300px;
        transform-style: preserve-3d;
        transition: transform 0.6s;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 12px;
    }

    .card.flipped {
        transform: rotateY(180deg);
    }

    .card-front,
    .card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        padding: 2rem;
        box-sizing: border-box;
        background: white;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .card-back {
        transform: rotateY(180deg);
        overflow-y: auto;
        justify-content: flex-start;
        align-items: flex-start;
        text-align: left;
    }

    .category {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #eee;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8em;
        color: #666;
    }

    .hint {
        margin-top: 2rem;
        font-size: 0.9em;
        color: #999;
        font-style: italic;
    }

    pre {
        background: #f4f4f4;
        padding: 1rem;
        border-radius: 4px;
        width: 100%;
        overflow-x: auto;
        margin-top: 1rem;
    }

    code {
        font-family: monospace;
    }
</style>
