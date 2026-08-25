"use client";

import { useEffect, useState } from "react";
import { CalendarClock, ListChecks, AlertTriangle, MessagesSquare, Scale } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { DashboardSummary } from "@/types";
import { Card, LoadingState, ErrorState } from "@/components/ui/primitives";
import { PriorityBadge } from "@/components/ui/badge";
import { formatDate, daysAgo } from "@/lib/utils";

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

const STATS = [
  { key: "high_priority_count", label: "High priority", icon: ListChecks },
  { key: "meetings_today_count", label: "Meetings today", icon: CalendarClock },
  { key: "overdue_count", label: "Overdue", icon: AlertTriangle },
  { key: "stale_follow_ups_count", label: "Follow-ups waiting", icon: MessagesSquare },
  { key: "pending_decisions_count", label: "Decisions pending", icon: Scale },
] as const;

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    setError(null);
    api.dashboard
      .summary()
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not reach the server."))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  return (
    <div className="px-8 py-8 max-w-6xl">
      <header className="mb-6">
        <p className="text-xs uppercase tracking-wide text-ink-500 font-medium">
          {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
        </p>
        <h1 className="mt-1 font-display text-3xl text-ink-900">{greeting()}, Alex</h1>
      </header>

      {loading && <LoadingState label="Preparing your briefing…" />}
      {error && <ErrorState message={error} onRetry={load} />}

      {data && (
        <>
          {/* Signature element: the briefing memo */}
          <Card className="mb-6 relative overflow-hidden border-l-4 border-l-brass px-6 py-5">
            <p className="text-xs uppercase tracking-wide text-brass-dark font-medium mb-1.5">
              Recommended focus
            </p>
            {data.recommended_focus ? (
              <p className="font-display italic text-xl text-ink-900 leading-snug">
                {data.recommended_focus}
              </p>
            ) : (
              <p className="font-display italic text-xl text-ink-900 leading-snug">
                Nothing urgent on the board — a good day to get ahead.
              </p>
            )}
            <p className="mt-3 text-sm text-ink-500">
              You have {data.high_priority_count} high-priority item
              {data.high_priority_count === 1 ? "" : "s"}, {data.meetings_today_count} meeting
              {data.meetings_today_count === 1 ? "" : "s"} today
              {data.overdue_count > 0 && `, and ${data.overdue_count} overdue item${data.overdue_count === 1 ? "" : "s"}`}.
            </p>
          </Card>

          {/* Stat strip */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
            {STATS.map(({ key, label, icon: Icon }) => (
              <Card key={key} className="px-4 py-3.5">
                <div className="flex items-center justify-between">
                  <Icon size={15} className="text-ink-500" strokeWidth={1.75} />
                  <span className="font-display text-2xl text-ink-900">{data[key]}</span>
                </div>
                <p className="mt-1.5 text-xs text-ink-500">{label}</p>
              </Card>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card className="p-5">
              <h2 className="font-medium text-ink-900 mb-3 flex items-center gap-2">
                <ListChecks size={16} className="text-brass" /> Top priorities
              </h2>
              {data.high_priority_tasks.length === 0 ? (
                <p className="text-sm text-ink-500 py-3">No high-priority tasks open right now.</p>
              ) : (
                <ul className="space-y-2.5">
                  {data.high_priority_tasks.map((t) => (
                    <li key={t.id} className="flex items-start justify-between gap-3 text-sm">
                      <div>
                        <p className="text-ink-900 font-medium">{t.title}</p>
                        <p className="text-ink-500 text-xs mt-0.5">Due {formatDate(t.due_date)}</p>
                      </div>
                      <PriorityBadge priority={t.priority} />
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card className="p-5">
              <h2 className="font-medium text-ink-900 mb-3 flex items-center gap-2">
                <CalendarClock size={16} className="text-brass" /> Today&apos;s meetings
              </h2>
              {data.todays_meetings.length === 0 ? (
                <p className="text-sm text-ink-500 py-3">Nothing on the calendar today.</p>
              ) : (
                <ul className="space-y-2.5">
                  {data.todays_meetings.map((m) => (
                    <li key={m.id} className="flex items-start justify-between gap-3 text-sm">
                      <div>
                        <p className="text-ink-900 font-medium">{m.title}</p>
                        <p className="text-ink-500 text-xs mt-0.5">{m.participants.join(", ")}</p>
                      </div>
                      <span className="font-mono text-xs text-ink-500">{m.time}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card className="p-5">
              <h2 className="font-medium text-ink-900 mb-3 flex items-center gap-2">
                <AlertTriangle size={16} className="text-brass" /> Overdue
              </h2>
              {data.overdue_tasks.length === 0 ? (
                <p className="text-sm text-ink-500 py-3">Nothing overdue. Nicely done.</p>
              ) : (
                <ul className="space-y-2.5">
                  {data.overdue_tasks.map((t) => (
                    <li key={t.id} className="flex items-start justify-between gap-3 text-sm">
                      <p className="text-ink-900 font-medium">{t.title}</p>
                      <span className="text-xs text-priority-critical font-medium">
                        {formatDate(t.due_date)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card className="p-5">
              <h2 className="font-medium text-ink-900 mb-3 flex items-center gap-2">
                <MessagesSquare size={16} className="text-brass" /> Follow-ups needing attention
              </h2>
              {data.stale_follow_ups.length === 0 ? (
                <p className="text-sm text-ink-500 py-3">Nothing has gone stale.</p>
              ) : (
                <ul className="space-y-2.5">
                  {data.stale_follow_ups.map((f) => (
                    <li key={f.id} className="flex items-start justify-between gap-3 text-sm">
                      <div>
                        <p className="text-ink-900 font-medium">
                          {f.person}
                          {f.organization && <span className="text-ink-500"> — {f.organization}</span>}
                        </p>
                        <p className="text-ink-500 text-xs mt-0.5">{f.topic}</p>
                      </div>
                      <span className="text-xs text-priority-high font-medium whitespace-nowrap">
                        {daysAgo(f.last_contact_date)}d ago
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
