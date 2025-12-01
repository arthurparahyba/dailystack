<script>
    import { createEventDispatcher } from "svelte";

    export let showAnswer = false;

    const dispatch = createEventDispatcher();
</script>

<div class="controls">
    <button on:click={() => dispatch("toggle")}>
        {showAnswer ? "Hide Answer" : "Show Answer"}
    </button>

    <button class="secondary" on:click={() => dispatch("next")}>
        Next Card
    </button>
</div>

<style>
    .controls {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1rem;
    }

    button {
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        background-color: #ff3e00;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    button:hover {
        background-color: #e63800;
    }

    button.secondary {
        background-color: #666;
    }

    button.secondary:hover {
        background-color: #555;
    }
</style>
