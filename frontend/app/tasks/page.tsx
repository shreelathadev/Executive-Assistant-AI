"use client";

import { useEffect, useState } from "react";
import { Plus, Check, Trash2, ListChecks } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { Task, Priority, TaskStatus } from "@/types";
import { Card, Button, LoadingState, ErrorState, EmptyState } from "@/components/ui/primitives";
import { PriorityBadge, StatusBadge } from "@/components/ui/badge";
import { cn, formatDate, isOverdue } from "@/lib/utils";

const PRIORITY_OPTIONS: Priority[] = ["critical", "high", "medium", "low"];
const STATUS_OPTIONS: TaskStatus[] = ["todo", "in_progress", "waiting", "completed"];

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [sortBy, setSortBy] = useState<"priority" | "due_date">("priority");
  const [showForm, setShowForm] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  function load() {
    setLoading(true);
    setError(null);
    api.tasks
      .list({ status: statusFilter === "all" ? undefined : statusFilter, sort_by: sortBy })
      .then(setTasks)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not reach the server."))
      .finally(() => setLoading(false));
  }

  useEffect(load, [statusFilter, sortBy]);

  async function handleComplete(id: number) {
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, status: "completed" } : t)));
    try {
      await api.tasks.complete(id);
    } catch {
      load();
    }
  }

  async function handleDelete(id: number) {
    setConfirmDeleteId(null);
    setTasks((prev) => prev.filter((t) => t.id !== id));
    try {
      await api.tasks.delete(id);
    } catch {
      load();
    }
  }

  return (
    <div className="px-8 py-8 max-w-6xl">
      <header className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl text-ink-900">Tasks</h1>
          <p className="mt-1 text-sm text-ink-500">Everything on your plate, ranked by what matters.</p>
        </div>
        <Button onClick={() => setShowForm((s) => !s)}>
          <Plus size={16} /> New task
        </Button>
      </header>

      {showForm && (
        <NewTaskForm
          onCreated={(t) => {
            setTasks((prev) => [t, ...prev]);
            setShowForm(false);
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      <div className="mb-4 flex items-center gap-2 flex-wrap">
        {(["all", ...STATUS_OPTIONS] as const).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              statusFilter === s
                ? "bg-ink-900 text-white border-ink-900"
                : "bg-surface-card text-ink-700 border-surface-border hover:bg-surface"
            )}
          >
            {s === "all" ? "All" : s.replace("_", " ")}
          </button>
        ))}
        <span className="mx-1 h-4 w-px bg-surface-border" />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as "priority" | "due_date")}
          className="rounded-full border border-surface-border bg-surface-card px-3 py-1 text-xs font-medium text-ink-700"
        >
          <option value="priority">Sort by priority</option>
          <option value="due_date">Sort by due date</option>
        </select>
      </div>

      {loading && <LoadingState label="Loading tasks…" />}
      {error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && tasks.length === 0 && (
        <EmptyState
          icon={ListChecks}
          title="No tasks here"
          description="Nothing matches this filter. Try another view, or add a new task."
          action={<Button onClick={() => setShowForm(true)}>Add a task</Button>}
        />
      )}

      {!loading && !error && tasks.length > 0 && (
        <Card className="overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border text-left text-xs text-ink-500">
                <th className="px-5 py-3 font-medium">Task</th>
                <th className="px-5 py-3 font-medium">Priority</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Due</th>
                <th className="px-5 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id} className="border-b border-surface-border last:border-0 hover:bg-surface/60">
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-ink-900">{t.title}</p>
                    {t.description && (
                      <p className="text-xs text-ink-500 mt-0.5 line-clamp-1">{t.description}</p>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <PriorityBadge priority={t.priority} />
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={t.status} />
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={cn(
                        "text-xs font-mono",
                        isOverdue(t.due_date, t.status) ? "text-priority-critical font-medium" : "text-ink-500"
                      )}
                    >
                      {formatDate(t.due_date)}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex justify-end gap-1.5">
                      {t.status !== "completed" && (
                        <button
                          onClick={() => handleComplete(t.id)}
                          title="Mark complete"
                          className="rounded-md p-1.5 text-ink-500 hover:bg-state-success/10 hover:text-state-success transition-colors"
                        >
                          <Check size={15} />
                        </button>
                      )}
                      {confirmDeleteId === t.id ? (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleDelete(t.id)}
                            className="text-xs font-medium text-state-danger px-1.5"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmDeleteId(null)}
                            className="text-xs font-medium text-ink-500 px-1.5"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDeleteId(t.id)}
                          title="Delete"
                          className="rounded-md p-1.5 text-ink-500 hover:bg-state-danger/10 hover:text-state-danger transition-colors"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}

function NewTaskForm({
  onCreated,
  onCancel,
}: {
  onCreated: (t: Task) => void;
  onCancel: () => void;
}) {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [dueDate, setDueDate] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) {
      setFormError("Give the task a title.");
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      const task = await api.tasks.create({
        title: title.trim(),
        priority,
        due_date: dueDate || undefined,
        description: description.trim() || undefined,
      });
      onCreated(task);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Could not create the task.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="mb-5 p-5">
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          autoFocus
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task title"
          className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          rows={2}
          className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
        />
        <div className="flex gap-3 flex-wrap">
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
            className="rounded-md border border-surface-border px-3 py-2 text-sm"
          >
            {PRIORITY_OPTIONS.map((p) => (
              <option key={p} value={p}>
                {p[0].toUpperCase() + p.slice(1)} priority
              </option>
            ))}
          </select>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="rounded-md border border-surface-border px-3 py-2 text-sm"
          />
        </div>
        {formError && <p className="text-sm text-state-danger">{formError}</p>}
        <div className="flex gap-2 pt-1">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Adding…" : "Add task"}
          </Button>
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}
