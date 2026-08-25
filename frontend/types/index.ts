//frontend/types/index.ts
export type Priority = "critical" | "high" | "medium" | "low";
export type TaskStatus = "todo" | "in_progress" | "waiting" | "completed";
export type FollowUpStatus = "waiting" | "responded" | "closed";
export type DecisionStatus = "pending" | "decided";

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  priority: Priority;
  status: TaskStatus;
  due_date?: string | null;
  project_id?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
  priority?: Priority;
  status?: TaskStatus;
  due_date?: string;
  project_id?: number;
  notes?: string;
}

export interface Meeting {
  id: number;
  user_id: number;
  title: string;
  date: string;
  time: string;
  participants: string[];
  description?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface FollowUp {
  id: number;
  user_id: number;
  person: string;
  organization?: string | null;
  topic: string;
  last_contact_date: string;
  expected_response_date?: string | null;
  status: FollowUpStatus;
  notes?: string | null;
  created_at: string;
}

export interface Decision {
  id: number;
  user_id: number;
  title: string;
  context?: string | null;
  options: string[];
  ai_recommendation?: {
    recommendation: string;
    reasoning: string;
    risks: string;
    factors: string;
  } | null;
  final_choice?: string | null;
  status: DecisionStatus;
  created_at: string;
}

export interface MeetingBrief {
  meeting: Meeting;
  open_tasks: Task[];
  relevant_follow_ups: FollowUp[];
  pending_decisions: Decision[];
  objective: string;
  talking_points: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
}

export interface PendingAction {
  pending_id: string;
  tool_name: string;
  description: string;
  args: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  reply?: string | null;
  pending_action?: PendingAction | null;
}

export interface DashboardSummary {
  high_priority_count: number;
  meetings_today_count: number;
  overdue_count: number;
  stale_follow_ups_count: number;
  pending_decisions_count: number;
  recommended_focus: string | null;
  high_priority_tasks: Task[];
  todays_meetings: Meeting[];
  overdue_tasks: Task[];
  stale_follow_ups: FollowUp[];
  pending_decisions: Decision[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message?: string | null;
}

export interface ConversationDetail {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: {
    id: string | number;
    role: "user" | "assistant";
    text: string;
    created_at: string;
  }[];
  pending_action?: PendingAction | null;
}

export interface NotesExtractResult {
  summary: string;
  action_items: {
    owner: string;
    assignee_type: "me" | "other";
    action: string;
    due_date: string | null;
    due_text: string | null;
  }[];
  decisions: {
    title: string;
    detail: string | null;
  }[];
}

export interface SaveActionItem {
  owner: string;
  action: string;
  create_as: "task" | "follow_up" | "none";
  due_date?: string | null;
  due_text?: string | null;
}

export interface SaveDecisionItem {
  title: string;
  detail?: string | null;
  save: boolean;
}

export interface NotesSaveResult {
  meeting_note_id: number;
  created_task_ids: number[];
  created_follow_up_ids: number[];
  created_decision_ids: number[];
}

