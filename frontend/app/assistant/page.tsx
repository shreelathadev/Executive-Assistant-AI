"use client";

import ChatWindow from "@/components/assistant/ChatWindow";

export default function AssistantPage() {
  return (
    <div className="px-6 py-6 h-full flex flex-col">
      <header className="mb-4 shrink-0">
        <h1 className="font-display text-2xl text-ink-900">Assistant</h1>
        <p className="mt-0.5 text-xs text-ink-500">Ask about your priorities, meetings, follow-ups, and decisions.</p>
      </header>
      <div className="flex-1 min-h-0">
        <ChatWindow />
      </div>
    </div>
  );
}

