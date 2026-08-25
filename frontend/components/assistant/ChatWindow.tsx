//frontend/components/assistant/ChatWindow.tsx
"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  Send,
  Sparkles,
  ShieldAlert,
  Plus,
  MessageSquare,
  Trash2,
  Clock,
  ChevronRight,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, ApiError } from "@/lib/api";
import type { ChatMessage, PendingAction, ConversationSummary } from "@/types";
import { Card, Button, LoadingState } from "@/components/ui/primitives";
import { cn, formatDate } from "@/lib/utils";

const STORAGE_KEY = "ea_active_conversation_id";

const MARKDOWN_COMPONENTS = {
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-1.5 last:mb-0">{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong className="font-semibold text-ink-900">{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="list-disc pl-4 space-y-0.5 mb-1.5 last:mb-0">{children}</ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="list-decimal pl-4 space-y-0.5 mb-1.5 last:mb-0">{children}</ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => <li>{children}</li>,
  h1: ({ children }: { children?: React.ReactNode }) => (
    <p className="font-semibold text-ink-900 mt-2.5 mb-1 first:mt-0">{children}</p>
  ),
  h2: ({ children }: { children?: React.ReactNode }) => (
    <p className="font-semibold text-ink-900 mt-2.5 mb-1 first:mt-0">{children}</p>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <p className="font-semibold text-ink-900 mt-2 mb-1 first:mt-0">{children}</p>
  ),
  code: ({ children }: { children?: React.ReactNode }) => (
    <code className="bg-surface px-1 py-0.5 rounded text-xs font-mono text-ink-700">{children}</code>
  ),
  a: ({ href, children }: { href?: string; children?: React.ReactNode }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-brass-dark underline underline-offset-2">
      {children}
    </a>
  ),
};

function AssistantMarkdown({ text }: { text: string }) {
  return (
    <div className="text-sm leading-relaxed">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
        {text}
      </ReactMarkdown>
    </div>
  );
}

const SUGGESTIONS = [
  "What's important today?",
  "Which tasks are overdue?",
  "Who am I waiting for?",
  "What decisions are pending?",
];

let idCounter = 0;
function nextId() {
  idCounter += 1;
  return `temp-${Date.now()}-${idCounter}`;
}

export default function ChatWindow() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState<PendingAction | null>(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending, loading]);

  const loadConversations = useCallback(async () => {
    try {
      const list = await api.assistant.listConversations();
      setConversations(list);
      return list;
    } catch {
      return [];
    }
  }, []);

  const loadConversation = useCallback(async (id: string) => {
    setHistoryLoading(true);
    setError(null);
    try {
      const detail = await api.assistant.getConversation(id);
      setConversationId(detail.id);
      localStorage.setItem(STORAGE_KEY, detail.id);
      setMessages(
        detail.messages.map((m) => ({
          id: String(m.id),
          role: m.role,
          text: m.text,
        }))
      );
      setPending(detail.pending_action || null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't load conversation.");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // Initial load: fetch list and restore active conversation if saved
  useEffect(() => {
    let mounted = true;
    (async () => {
      const list = await loadConversations();
      if (!mounted) return;

      const savedId = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      if (savedId && list.some((c) => c.id === savedId)) {
        loadConversation(savedId);
      } else if (list.length > 0) {
        loadConversation(list[0].id);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [loadConversations, loadConversation]);

  function startNewChat() {
    setConversationId(null);
    setMessages([]);
    setPending(null);
    setError(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  async function handleDeleteConversation(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    try {
      await api.assistant.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (conversationId === id) {
        startNewChat();
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to delete conversation.");
    } finally {
      setDeletingId(null);
    }
  }

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { id: nextId(), role: "user", text: trimmed }]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      const res = await api.assistant.chat(conversationId, trimmed);
      setConversationId(res.conversation_id);
      localStorage.setItem(STORAGE_KEY, res.conversation_id);

      if (res.pending_action) {
        setPending(res.pending_action);
      } else if (res.reply) {
        setMessages((prev) => [...prev, { id: nextId(), role: "assistant", text: res.reply as string }]);
      }
      // Refresh list to update titles/ordering
      loadConversations();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't reach the assistant.");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm(approve: boolean) {
    if (!pending || !conversationId) return;
    const current = pending;
    setPending(null);
    setLoading(true);
    setError(null);

    if (!approve) {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", text: "Cancelled — I didn't make that change." },
      ]);
    }

    try {
      const res = await api.assistant.confirm(conversationId, current.pending_id, approve);
      if (res.pending_action) {
        setPending(res.pending_action);
      } else if (res.reply) {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), role: "assistant", text: res.reply as string },
        ]);
      }
      loadConversations();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't reach the assistant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 h-[calc(100vh-9.5rem)]">
      {/* Conversation History Sidebar */}
      <Card className="hidden md:flex flex-col h-full overflow-hidden border-surface-border p-0">
        <div className="p-3 border-b border-surface-border flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-ink-500">History</span>
          <Button
            onClick={startNewChat}
            className="text-xs h-7 px-2.5 py-1 gap-1"
          >
            <Plus size={13} /> New chat
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 px-4 text-xs text-ink-500">
              No previous chats yet. Start a conversation to save history.
            </div>
          ) : (
            conversations.map((c) => {
              const active = conversationId === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => loadConversation(c.id)}
                  className={cn(
                    "group relative flex items-start justify-between rounded-lg p-2.5 text-xs transition-all cursor-pointer",
                    active
                      ? "bg-surface border border-brass/40 text-ink-900 font-medium shadow-sm"
                      : "text-ink-700 hover:bg-surface/80 hover:text-ink-900"
                  )}
                >
                  <div className="flex-1 min-w-0 pr-2">
                    <div className="flex items-center gap-1.5">
                      <MessageSquare
                        size={12}
                        className={active ? "text-brass-dark shrink-0" : "text-ink-400 shrink-0"}
                      />
                      <span className="truncate block font-medium">{c.title}</span>
                    </div>
                    {c.last_message && (
                      <p className="mt-1 text-[11px] text-ink-500 line-clamp-1 truncate">
                        {c.last_message}
                      </p>
                    )}
                    <div className="mt-1.5 flex items-center gap-1 text-[10px] text-ink-400">
                      <Clock size={10} />
                      <span>{formatDate(c.updated_at)}</span>
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center pt-0.5">
                    {deletingId === c.id ? (
                      <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={(e) => handleDeleteConversation(e, c.id)}
                          className="text-[10px] text-state-danger font-medium hover:underline"
                        >
                          Del
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeletingId(null);
                          }}
                          className="text-[10px] text-ink-500"
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeletingId(c.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 text-ink-400 hover:text-state-danger p-1 transition-opacity"
                        title="Delete chat"
                      >
                        <Trash2 size={12} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </Card>

      {/* Main Chat Interface */}
      <div className="md:col-span-3 flex flex-col h-full border border-surface-border bg-surface-card rounded-xl overflow-hidden p-4">
        {/* Mobile Header / Switcher */}
        <div className="md:hidden flex items-center justify-between pb-3 mb-2 border-b border-surface-border">
          <span className="text-xs font-medium text-ink-700 truncate">
            {conversations.find((c) => c.id === conversationId)?.title || "New Chat"}
          </span>
          <Button onClick={startNewChat} className="text-xs h-7 px-2 py-1 gap-1">
            <Plus size={12} /> New
          </Button>
        </div>

        {/* Message Container */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto pr-1 space-y-4 pb-4">
          {historyLoading ? (
            <div className="h-full flex items-center justify-center py-12">
              <LoadingState label="Loading conversation history…" />
            </div>
          ) : (
            <>
              {messages.length === 0 && !pending && (
                <div className="pt-6 pb-2">
                  <div className="mb-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-brass-dark mb-1">
                      NovaTech Executive Assistant
                    </p>
                    <p className="text-sm text-ink-700">
                      I can help review today&apos;s schedule, identify overdue deliverables, summarize follow-ups, and run confirmation-gated updates.
                    </p>
                  </div>
                  <p className="text-xs text-ink-500 mb-2">Try asking:</p>
                  <div className="flex flex-wrap gap-2">
                    {SUGGESTIONS.map((s) => (
                      <button
                        key={s}
                        onClick={() => send(s)}
                        className="rounded-full border border-surface-border bg-surface px-3.5 py-1.5 text-xs text-ink-700 hover:border-brass hover:text-brass-dark transition-colors flex items-center gap-1.5"
                      >
                        {s} <ChevronRight size={11} className="text-ink-400" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
                >
                  <div
                    className={cn(
                      "max-w-[85%] rounded-xl px-4 py-2.5",
                      m.role === "user"
                        ? "bg-ink-900 text-white text-sm leading-relaxed"
                        : "bg-surface border border-surface-border text-ink-900"
                    )}
                  >
                    {m.role === "assistant" ? <AssistantMarkdown text={m.text} /> : m.text}
                  </div>
                </div>
              ))}

              {pending && (
                <Card className="border-l-4 border-l-brass px-5 py-4 max-w-[90%] bg-surface">
                  <div className="flex items-start gap-2.5">
                    <ShieldAlert size={16} className="text-brass-dark mt-0.5 shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs uppercase tracking-wide text-brass-dark font-medium mb-1">
                        Needs your confirmation
                      </p>
                      <p className="text-sm text-ink-900 font-medium">{pending.description}</p>
                      <div className="mt-3 flex gap-2">
                        <Button className="text-xs px-3 py-1.5" onClick={() => handleConfirm(true)} disabled={loading}>
                          Confirm
                        </Button>
                        <Button
                          className="text-xs px-3 py-1.5"
                          variant="secondary"
                          onClick={() => handleConfirm(false)}
                          disabled={loading}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {loading && (
                <div className="flex items-center gap-2 text-xs text-ink-500 px-1 py-1">
                  <Sparkles size={13} className="text-brass animate-pulse" />
                  Thinking…
                </div>
              )}

              {error && <p className="text-xs text-state-danger px-1">{error}</p>}
            </>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex items-center gap-2 border-t border-surface-border pt-3 mt-auto shrink-0"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your priorities, meetings, follow-ups, or decisions…"
            disabled={!!pending || historyLoading}
            className="flex-1 rounded-md border border-surface-border bg-surface px-3.5 py-2 text-sm focus:border-brass disabled:opacity-50"
          />
          <Button type="submit" disabled={loading || !!pending || !input.trim() || historyLoading}>
            <Send size={14} />
          </Button>
        </form>
      </div>
    </div>
  );
}

