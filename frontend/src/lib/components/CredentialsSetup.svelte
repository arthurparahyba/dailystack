<script>
    import { onMount } from "svelte";

    let configured = false;
    let missing = [];
    let loading = true;

    onMount(async () => {
        try {
            const response = await fetch("/api/check-credentials");
            const data = await response.json();
            configured = data.configured;
            missing = data.missing || [];
        } catch (error) {
            console.error("Failed to check credentials:", error);
        } finally {
            loading = false;
        }
    });

    function openStackSpotProfile() {
        window.open("https://myaccount.stackspot.com/profile", "_blank");
    }
</script>

{#if loading}
    <div class="flex items-center justify-center h-screen bg-gray-900">
        <div
            class="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"
        ></div>
    </div>
{:else if !configured}
    <div
        class="flex flex-col items-center justify-center h-screen bg-gray-900 p-8"
    >
        <div
            class="max-w-2xl w-full bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700"
        >
            <div class="flex items-center gap-3 mb-6">
                <svg
                    class="w-8 h-8 text-orange-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                </svg>
                <h1 class="text-2xl font-bold text-white">
                    Configuração Necessária
                </h1>
            </div>

            <p class="text-gray-300 mb-6">
                Para usar o Dailystack, você precisa configurar as seguintes
                variáveis de ambiente no seu sistema operacional:
            </p>

            <div class="bg-gray-900 rounded-lg p-4 mb-6 font-mono text-sm">
                {#each missing as variable}
                    <div class="text-red-400 mb-1">❌ {variable}</div>
                {/each}
            </div>

            <div
                class="bg-blue-900/30 border border-blue-700 rounded-lg p-4 mb-6"
            >
                <h2
                    class="text-blue-300 font-semibold mb-2 flex items-center gap-2"
                >
                    <svg
                        class="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    Como obter as credenciais:
                </h2>
                <ol class="text-gray-300 space-y-2 ml-7 list-decimal">
                    <li>Acesse sua conta StackSpot</li>
                    <li>Clique em "Access Token"</li>
                    <li>Copie os valores de Client ID, Client Key e Realm</li>
                    <li>
                        Configure-os como variáveis de ambiente no seu sistema
                    </li>
                </ol>
            </div>

            <button
                on:click={openStackSpotProfile}
                class="w-full px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-semibold transition-all transform hover:scale-105 shadow-lg flex items-center justify-center gap-2"
            >
                <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                </svg>
                Abrir StackSpot Profile
            </button>

            <p class="text-gray-400 text-sm mt-4 text-center">
                Após configurar as variáveis, reinicie a aplicação.
            </p>
        </div>
    </div>
{:else}
    <slot />
{/if}
