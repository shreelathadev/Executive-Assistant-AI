import { cn } from "@/lib/utils";
import type { Priority, TaskStatus, FollowUpStatus, DecisionStatus } from "@/types";

const PRIORITY_STYLES: Record<Priority, string> = {
  critical: "bg-priority-critical/10 text-priority-critical border-priority-critical/20",
  high: "bg-priority-high/10 text-priority-high border-priority-high/20",
  medium: "bg-priority-medium/10 text-priority-medium border-priority-medium/20",
  low: "bg-priority-low/10 text-priority-low border-priority-low/20",
};

const PRIORITY_LABEL: Record<Priority, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        PRIORITY_STYLES[priority]
      )}
    >
      {PRIORITY_LABEL[priority]}
    </span>
  );
}

const STATUS_STYLES: Record<TaskStatus, string> = {
  todo: "bg-surface border-surface-border text-ink-700",
  in_progress: "bg-priority-medium/10 text-priority-medium border-priority-medium/20",
  waiting: "bg-priority-high/10 text-priority-high border-priority-high/20",
  completed: "bg-state-success/10 text-state-success border-state-success/20",
};

const STATUS_LABEL: Record<TaskStatus, string> = {
  todo: "To do",
  in_progress: "In progress",
  waiting: "Waiting",
  completed: "Completed",
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        STATUS_STYLES[status]
      )}
    >
      {STATUS_LABEL[status]}
    </span>
  );
}

const FOLLOWUP_STATUS_LABEL: Record<FollowUpStatus, string> = {
  waiting: "Waiting",
  responded: "Responded",
  closed: "Closed",
};

const FOLLOWUP_STATUS_STYLES: Record<FollowUpStatus, string> = {
  waiting: "bg-priority-high/10 text-priority-high border-priority-high/20",
  responded: "bg-state-success/10 text-state-success border-state-success/20",
  closed: "bg-surface border-surface-border text-ink-700",
};

export function FollowUpStatusBadge({ status }: { status: FollowUpStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        FOLLOWUP_STATUS_STYLES[status]
      )}
    >
      {FOLLOWUP_STATUS_LABEL[status]}
    </span>
  );
}

const DECISION_STATUS_LABEL: Record<DecisionStatus, string> = {
  pending: "Pending",
  decided: "Decided",
};

export function DecisionStatusBadge({ status }: { status: DecisionStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        status === "pending"
          ? "bg-priority-high/10 text-priority-high border-priority-high/20"
          : "bg-state-success/10 text-state-success border-state-success/20"
      )}
    >
      {DECISION_STATUS_LABEL[status]}
    </span>
  );
}
