<script>
  import { onMount } from "svelte";
  import Header from "./lib/components/Header.svelte";
  import Flashcard from "./lib/components/Flashcard.svelte";
  import Controls from "./lib/components/Controls.svelte";
  import {
    scenario,
    flashcard,
    loading,
    error,
    showAnswer,
    loadDailyChallenge,
    toggleAnswer,
    nextCard,
  } from "./lib/store";

  onMount(async () => {
    await loadDailyChallenge();
  });
</script>

<main class="container">
  <Header scenario={$scenario} />

  {#if $loading}
    <div class="loading">Loading today's challenge...</div>
  {:else if $error}
    <div class="error">Error: {$error}</div>
  {:else if $flashcard}
    <Flashcard
      flashcard={$flashcard}
      showAnswer={$showAnswer}
      on:toggle={toggleAnswer}
    />

    <Controls
      showAnswer={$showAnswer}
      on:toggle={toggleAnswer}
      on:next={nextCard}
    />
  {:else}
    <div class="no-data">No flashcards available.</div>
  {/if}
</main>

<style>
  :global(body) {
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f9f9f9;
    color: #333;
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  .loading,
  .error,
  .no-data {
    text-align: center;
    margin-top: 3rem;
    font-size: 1.2rem;
  }

  .error {
    color: #d32f2f;
  }
</style>
