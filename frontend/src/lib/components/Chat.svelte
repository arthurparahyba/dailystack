<script lang="ts">
    import { onMount, beforeUpdate, afterUpdate } from "svelte";
    import { fetchChatHistory } from "../api";
    import { messages, isGenerating } from "../store";
    import { marked } from "marked";
    import DOMPurify from "dompurify";

    export let showAnswer = false;

    let newMessage = "";
    let chatContainer;
    let autoscroll = false;

    onMount(async () => {
        try {
            const history = await fetchChatHistory();
            messages.set(history);
        } catch (e) {
            console.error("Failed to load chat history", e);
        }
    });

    beforeUpdate(() => {
        if (chatContainer) {
            const scrollableDistance =
                chatContainer.scrollHeight - chatContainer.offsetHeight;
            const currentScroll = chatContainer.scrollTop;
            // If user is within 50px of the bottom, enable autoscroll
            autoscroll = currentScroll > scrollableDistance - 50;
        }
    });

    afterUpdate(() => {
        if (autoscroll && chatContainer) {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: "smooth",
            });
        }
    });

    function formatContent(content) {
        if (!content) return "";
        try {
            // Parse markdown to HTML
            const rawHtml = marked.parse(content, { async: false }) as string;
            // Sanitize HTML
            return DOMPurify.sanitize(rawHtml);
        } catch (e) {
            console.error("Error parsing markdown", e);
            return content;
        }
    }

    async function sendMessage() {
        if (!newMessage.trim() || $isGenerating) return;

        const userMsg = { role: "user", content: newMessage };
        messages.update((msgs) => [...msgs, userMsg]);
        const question = newMessage;
        newMessage = "";
        isGenerating.set(true);

        try {
            const response = await fetch("/api/ask-llm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) throw new Error("Failed to send message");

            // Create a placeholder for the bot response
            const botMsg = { role: "bot", content: "" };
            messages.update((msgs) => [...msgs, botMsg]);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split("\n\n");

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.answer) {
                                messages.update((msgs) => {
                                    const newMsgs = [...msgs];
                                    const lastMsg = newMsgs[newMsgs.length - 1];
                                    lastMsg.content += data.answer;
                                    return newMsgs;
                                });
                            }
                        } catch (e) {
                            console.error("Error parsing chunk", e);
                        }
                    }
                }
            }
        } catch (e) {
            console.error(e);
            messages.update((msgs) => [
                ...msgs,
                { role: "error", content: "Error: " + e.message },
            ]);
        } finally {
            isGenerating.set(false);
        }
    }

    function handleKeydown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }
</script>

<div
    class="flex flex-col h-full bg-gray-800 rounded-xl shadow-sm overflow-hidden border border-gray-700"
>
    <div
        class="flex-1 overflow-y-auto overflow-x-hidden p-4 flex flex-col gap-4"
        bind:this={chatContainer}
    >
        {#if $messages.length === 0}
            <div
                class="flex items-center justify-center h-full text-gray-400 italic"
            >
                <p>Ask a question about this flashcard!</p>
            </div>
        {/if}
        {#each $messages as msg, i}
            <div
                class="flex flex-col w-full {msg.role === 'user'
                    ? 'items-end'
                    : 'items-start'}"
            >
                <div
                    class="px-4 py-3 rounded-xl leading-relaxed relative overflow-hidden max-w-[85%] min-w-0 break-words whitespace-pre-wrap select-text markdown-content {msg.role ===
                    'user'
                        ? 'bg-orange-500 text-white rounded-br-sm'
                        : msg.role === 'bot'
                          ? 'bg-gray-700 text-gray-100 rounded-bl-sm'
                          : 'bg-red-900 text-red-200'} {msg.role === 'bot' &&
                    i === 0 &&
                    !showAnswer
                        ? 'bg-gray-600 cursor-not-allowed'
                        : ''}"
                >
                    {#if msg.role === "bot" && i === 0 && !showAnswer}
                        <div
                            class="absolute inset-0 flex items-center justify-center z-10 font-bold text-gray-600 bg-white/30"
                        >
                            <span>Show Answer to see details</span>
                        </div>
                        <div class="blur-sm select-none opacity-50">
                            {@html formatContent(msg.content)}
                        </div>
                    {:else}
                        {@html formatContent(msg.content)}
                    {/if}
                </div>
            </div>
        {/each}
        {#if $isGenerating}
            <div class="flex flex-col items-start">
                <div
                    class="px-4 py-3 rounded-xl bg-gray-700 text-gray-400 italic"
                >
                    ...
                </div>
            </div>
        {/if}
    </div>

    <div class="p-4 border-t border-gray-700 flex gap-2 bg-gray-800">
        <textarea
            bind:value={newMessage}
            on:keydown={handleKeydown}
            placeholder="Ask a question..."
            rows="1"
            class="flex-1 px-4 py-3 border border-gray-600 bg-gray-700 text-gray-100 placeholder-gray-400 rounded-full resize-none font-sans outline-none transition-colors focus:border-orange-500"
        ></textarea>
        <button
            on:click={sendMessage}
            disabled={$isGenerating || !newMessage.trim()}
            class="px-6 bg-orange-500 text-white rounded-full font-semibold transition-opacity hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
            Send
        </button>
    </div>
</div>

<style>
    /* Styles for markdown content within the chat */
    :global(.markdown-content h1) {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content h2) {
        font-size: 1.3em;
        font-weight: bold;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content h3) {
        font-size: 1.1em;
        font-weight: bold;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content p) {
        margin-bottom: 0.5em;
    }
    :global(.markdown-content ul) {
        list-style-type: disc;
        padding-left: 1.5em;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content ol) {
        list-style-type: decimal;
        padding-left: 1.5em;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content li) {
        margin-bottom: 0.25em;
    }
    :global(.markdown-content strong) {
        font-weight: bold;
        color: #fb923c; /* orange-400 */
    }
    :global(.markdown-content code) {
        background-color: #374151; /* gray-700 */
        padding: 0.1em 0.3em;
        border-radius: 0.25em;
        font-family: monospace;
        font-size: 0.9em;
    }
    :global(.markdown-content pre) {
        background-color: #1f2937; /* gray-800 */
        padding: 1em;
        border-radius: 0.5em;
        overflow-x: auto;
        margin-bottom: 0.5em;
        border: 1px solid #374151;
    }
    :global(.markdown-content pre code) {
        background-color: transparent;
        padding: 0;
        color: #e5e7eb; /* gray-200 */
    }
    :global(.markdown-content blockquote) {
        border-left: 4px solid #4b5563; /* gray-600 */
        padding-left: 1em;
        color: #9ca3af; /* gray-400 */
        font-style: italic;
        margin-bottom: 0.5em;
    }
    :global(.markdown-content a) {
        color: #fb923c;
        text-decoration: underline;
    }
    :global(.markdown-content hr) {
        border-color: #4b5563;
        margin: 1em 0;
    }
</style>
