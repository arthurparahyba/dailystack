<script lang="ts">
    import { Scenario } from "../models";
    export let scenario: Scenario | null = null;
</script>

<header>
    <h1>DailyStack</h1>
    <p class="subtitle">Your daily dose of dev knowledge</p>

    {#if scenario}
        <div class="scenario-info">
            <h2>{scenario.title}</h2>
            <p class="description">{scenario.description}</p>
            {#if scenario.context}
                <div class="context">
                    <strong>Context:</strong>
                    {scenario.context}
                </div>
            {/if}
        </div>
    {/if}
</header>

<style>
    header {
        text-align: center;
        margin-bottom: 2rem;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 3em;
        font-weight: 100;
        margin-bottom: 0.2em;
    }

    .subtitle {
        font-size: 1.2em;
        color: #666;
        margin-bottom: 1.5rem;
    }

    .scenario-info {
        background: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        max-width: 800px;
        margin: 0 auto;
        text-align: left;
        border-left: 4px solid #ff3e00;
    }

    .scenario-info h2 {
        margin-top: 0;
        color: #333;
        font-size: 1.5em;
    }

    .description {
        color: #555;
        line-height: 1.5;
    }

    .context {
        margin-top: 1rem;
        font-size: 0.9em;
        color: #666;
        background: #f9f9f9;
        padding: 0.8rem;
        border-radius: 4px;
    }
</style>
