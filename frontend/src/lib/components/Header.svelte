<script lang="ts">
    import { Scenario } from "../models";
    export let scenario: Scenario | null = null;
</script>

<header class="bg-gray-800 border-b border-gray-700 px-6 py-2">
    {#if scenario}
        <div class="flex flex-col gap-1">
            <h2
                class="m-0 text-gray-100 text-lg font-semibold flex items-center gap-2"
            >
                <span class="w-1 h-4 bg-orange-500 rounded-full"></span>
                {scenario.title}
            </h2>
            <p class="m-0 text-gray-300 text-sm leading-snug">
                {scenario.description}
            </p>
        </div>
    {/if}
</header>
