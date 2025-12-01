<script lang="ts">
    import { Scenario } from "../models";
    export let scenario: Scenario | null = null;
</script>

{#if scenario}
    <div class="scenario-container">
        <h2>{scenario.title}</h2>
        <p class="description">{scenario.description}</p>
        {#if scenario.context}
            <div class="context">
                <h3>Context</h3>
                <p>{scenario.context}</p>
            </div>
        {/if}
    </div>
{/if}

<style>
    .scenario-container {
        background: #f4f4f4;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 5px solid #ff3e00;
    }

    h2 {
        margin-top: 0;
        color: #333;
    }

    .description {
        font-size: 1.1em;
        color: #555;
    }

    .context {
        margin-top: 1rem;
        background: #fff;
        padding: 1rem;
        border-radius: 4px;
    }

    .context h3 {
        margin-top: 0;
        font-size: 1em;
        color: #666;
    }
</style>
