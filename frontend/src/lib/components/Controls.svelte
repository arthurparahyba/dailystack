<script>
    import { createEventDispatcher } from "svelte";

    export let showAnswer = false;

    const dispatch = createEventDispatcher();
</script>

<div class="flex justify-center gap-2 mt-2">
    <button
        on:click={() => dispatch("toggle")}
        class="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-full font-medium transition-colors"
    >
        {showAnswer ? "Hide Answer" : "Show Answer"}
    </button>

    <button
        class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-full font-medium transition-colors"
        on:click={() => dispatch("next")}
    >
        Next Card
    </button>
</div>
