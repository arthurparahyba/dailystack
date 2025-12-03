<script>
  import { onMount } from "svelte";
  import Header from "./lib/components/Header.svelte";
  import Flashcard from "./lib/components/Flashcard.svelte";
  import Controls from "./lib/components/Controls.svelte";
  import Chat from "./lib/components/Chat.svelte";
  import Scenario from "./lib/components/Scenario.svelte";
  import {
    scenario,
    flashcard,
    loading,
    error,
    showAnswer,
    hasStarted,
    loadDailyChallenge,
    toggleAnswer,
    nextCard,
    startChallenge,
  } from "./lib/store";

  onMount(async () => {
    await loadDailyChallenge();
  });
</script>

<div
  class="h-screen w-screen bg-gray-900 overflow-hidden"
  class:grid={$hasStarted}
  class:grid-rows-[auto_1fr]={$hasStarted}
>
  {#if $hasStarted}
    <Header scenario={$scenario} />
  {/if}

  <main class="overflow-hidden" class:h-full={!$hasStarted}>
    {#if $loading}
      <div class="flex flex-col items-center justify-center h-full gap-4">
        <div
          class="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"
        ></div>
        <p class="text-gray-300">Loading today's challenge...</p>
      </div>
    {:else if $error}
      <div class="flex flex-col items-center justify-center h-full gap-4">
        <p class="text-red-400">Error: {$error}</p>
        <button
          on:click={loadDailyChallenge}
          class="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-full font-medium transition-colors"
        >
          Retry
        </button>
      </div>
    {:else if $scenario && !$hasStarted}
      <!-- Start Screen -->
      <div class="flex flex-col items-center justify-center h-full p-8 gap-8">
        <div class="max-w-3xl w-full">
          <Scenario scenario={$scenario} featured={true} />
        </div>
        <button
          on:click={startChallenge}
          class="px-8 py-4 bg-orange-500 hover:bg-orange-600 text-white rounded-full font-bold text-lg transition-all transform hover:scale-105 shadow-lg"
        >
          Iniciar Desafio
        </button>
      </div>
    {:else if $flashcard && $hasStarted}
      <!-- Main Interface -->
      <div class="grid grid-cols-[30%_1fr] gap-4 p-4 h-full">
        <div class="flex flex-col gap-4">
          <div class="flex-1">
            <Flashcard
              flashcard={$flashcard}
              showAnswer={$showAnswer}
              on:toggle={toggleAnswer}
            />
          </div>

          <div>
            <Controls
              showAnswer={$showAnswer}
              on:toggle={toggleAnswer}
              on:next={nextCard}
            />
          </div>
        </div>

        <div class="h-full overflow-hidden">
          <Chat showAnswer={$showAnswer} />
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center h-full text-gray-400 italic">
        No flashcards available.
      </div>
    {/if}
  </main>
</div>
