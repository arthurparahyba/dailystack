<script lang="ts">
    import { Scenario } from "../models";
    export let scenario: Scenario | null = null;
    export let featured: boolean = false;
</script>

{#if scenario}
    <div class="scenario-container" class:featured>
        <h2>{scenario.title}</h2>
        <p class="description">{scenario.description}</p>
    </div>
{/if}

<style>
    .scenario-container {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 5px solid #f97316;
        border: 2px solid #374151;
    }

    .scenario-container.featured {
        padding: 3rem;
        border-radius: 16px;
        border: 3px solid #f97316;
        box-shadow: 0 20px 60px rgba(249, 115, 22, 0.3);
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    }

    h2 {
        margin-top: 0;
        color: #f9fafb;
        font-size: 1.5rem;
    }

    .featured h2 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .description {
        font-size: 1.1em;
        color: #d1d5db;
        line-height: 1.6;
    }

    .featured .description {
        font-size: 1.3em;
        color: #e5e7eb;
    }
</style>
