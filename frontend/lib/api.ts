//frontend/lib/api.ts
import type {
  Task,
  TaskCreateInput,
  Meeting,
  MeetingBrief,
  FollowUp,
  Decision,
  DashboardSummary,
  ChatResponse,
  ConversationSummary,
  ConversationDetail,
  NotesExtractResult,
  SaveActionItem,
  SaveDecisionItem,
  NotesSaveResult,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(body || res.statusText, res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export const api = {
  dashboard: {
    summary: () => request<DashboardSummary>("/api/dashboard/summary"),
  },
  tasks: {
    list: (params?: { status?: string; priority?: string; overdue_only?: boolean; sort_by?: string }) => {
      const qs = new URLSearchParams();
      if (params?.status) qs.set("status", params.status);
      if (params?.priority) qs.set("priority", params.priority);
      if (params?.overdue_only) qs.set("overdue_only", "true");
      if (params?.sort_by) qs.set("sort_by", params.sort_by);
      const suffix = qs.toString() ? `?${qs.toString()}` : "";
      return request<Task[]>(`/api/tasks${suffix}`);
    },
    create: (data: TaskCreateInput) =>
      request<Task>("/api/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Partial<TaskCreateInput>) =>
      request<Task>(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    complete: (id: number) =>
      request<Task>(`/api/tasks/${id}/complete`, { method: "POST" }),
    delete: (id: number) =>
      request<void>(`/api/tasks/${id}`, { method: "DELETE" }),
  },
  meetings: {
    list: (params?: { upcoming_only?: boolean }) => {
      const qs = new URLSearchParams();
      if (params?.upcoming_only) qs.set("upcoming_only", "true");
      const suffix = qs.toString() ? `?${qs.toString()}` : "";
      return request<Meeting[]>(`/api/meetings${suffix}`);
    },
    brief: (meetingId: number) => request<MeetingBrief>(`/api/meetings/${meetingId}/brief`),
  },
  followUps: {
    list: () => request<FollowUp[]>("/api/follow-ups").catch(() => [] as FollowUp[]),
    draft: (id: number) => request<{ draft_message: string }>(`/api/follow-ups/${id}/draft`, { method: "POST" }),
  },
  decisions: {
    list: () => request<Decision[]>("/api/decisions").catch(() => [] as Decision[]),
    recommend: (id: number) => request<Decision>(`/api/decisions/${id}/recommend`, { method: "POST" }),
  },
  meetingNotes: {
    extract: (rawText: string, meetingId?: number) =>
      request<NotesExtractResult>("/api/meeting-notes/extract", {
        method: "POST",
        body: JSON.stringify({ meeting_id: meetingId ?? null, raw_text: rawText }),
      }),
    save: (params: {
      rawText: string;
      summary: string;
      actionItems: SaveActionItem[];
      decisions: SaveDecisionItem[];
      meetingId?: number;
    }) =>
      request<NotesSaveResult>("/api/meeting-notes", {
        method: "POST",
        body: JSON.stringify({
          meeting_id: params.meetingId ?? null,
          raw_text: params.rawText,
          summary: params.summary,
          action_items: params.actionItems,
          decisions: params.decisions,
        }),
      }),
  },
  assistant: {
    listConversations: () => request<ConversationSummary[]>("/api/assistant/conversations"),
    getConversation: (id: string) => request<ConversationDetail>(`/api/assistant/conversations/${id}`),
    deleteConversation: (id: string) => request<void>(`/api/assistant/conversations/${id}`, { method: "DELETE" }),
    chat: (conversationId: string | null, message: string) =>
      request<ChatResponse>("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({ conversation_id: conversationId, message }),
      }),
    confirm: (conversationId: string, pendingId: string, approve: boolean) =>
      request<ChatResponse>("/api/assistant/confirm", {
        method: "POST",
        body: JSON.stringify({ conversation_id: conversationId, pending_id: pendingId, approve }),
      }),
  },
};

export { ApiError };