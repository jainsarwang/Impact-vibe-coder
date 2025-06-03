import { env } from "~/env";

import { type Message } from "../messaging";
import { fetchStream } from "../sse";

import { type ChatEvent } from "./types";

export function chatStream(
  userMessage: Message,
  messages: Message[],
  session_id: string,
  params: { deepThinkingMode: boolean; searchBeforePlanning: boolean },
  options: { abortSignal?: AbortSignal } = {},
) {
  return fetchStream<ChatEvent>(
    `${env.NEXT_PUBLIC_API_URL}/chat/stream?session_id=${session_id}`,
    {
      body: JSON.stringify({
        messages: [...messages, userMessage],
        deep_thinking_mode: params.deepThinkingMode,
        search_before_planning: params.searchBeforePlanning,
        debug:
          location.search.includes("debug") &&
          !location.search.includes("debug=false"),
      }),
      signal: options.abortSignal,
    },
  );
}
