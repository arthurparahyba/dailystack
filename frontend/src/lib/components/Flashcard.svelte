<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { Flashcard } from "../models";
    export let flashcard: Flashcard | null = null;
    export let showAnswer = false;

    const dispatch = createEventDispatcher();

    function handleClick() {
        if (!showAnswer) {
            dispatch("toggle");
        }
    }

    function handleKeydown(e) {
        if (e.key === "Enter" && !showAnswer) {
            dispatch("toggle");
        }
    }
</script>

<div class="h-full mb-0" style="perspective: 1000px;">
    <div
        class="relative w-full h-full rounded-xl shadow-lg transition-transform duration-[600ms] {!showAnswer
            ? 'cursor-pointer'
            : ''}"
        class:rotate-y-180={showAnswer}
        on:click={handleClick}
        on:keydown={handleKeydown}
        role="button"
        tabindex="0"
        style="transform-style: preserve-3d;"
    >
        <!-- Front of card (Question only) -->
        <div
            class="absolute inset-0 p-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex flex-col items-center justify-center text-center border-2 border-orange-400"
            style="-webkit-backface-visibility: hidden; backface-visibility: hidden;"
        >
            <span
                class="absolute top-4 right-4 bg-orange-700 bg-opacity-50 px-2 py-1 rounded text-xs text-white font-medium"
            >
                {flashcard.category || "General"}
            </span>
            <h2 class="text-xl font-semibold text-white">
                {flashcard.question}
            </h2>
            <p class="mt-8 text-sm text-orange-100 italic">
                Click to reveal answer
            </p>
        </div>

        <!-- Back of card (Question + Answer) -->
        <div
            class="absolute inset-0 p-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex flex-col justify-start items-start text-left overflow-y-auto border-2 border-orange-400"
            style="-webkit-backface-visibility: hidden; backface-visibility: hidden; transform: rotateY(180deg);"
        >
            <span
                class="absolute top-4 right-4 bg-orange-700 bg-opacity-50 px-2 py-1 rounded text-xs text-white font-medium"
            >
                {flashcard.category || "General"}
            </span>
            <h3 class="text-lg font-bold text-white mb-4">Question</h3>
            <p class="text-orange-50 mb-6">{flashcard.question}</p>

            <h3 class="text-lg font-bold text-white mb-2">Answer</h3>
            <p class="text-orange-50">{flashcard.answer}</p>
        </div>
    </div>
</div>

<style>
    .rotate-y-180 {
        transform: rotateY(180deg);
    }
</style>
