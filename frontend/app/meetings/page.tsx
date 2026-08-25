"use client";

import { useEffect, useState } from "react";
import { CalendarClock, Users, Sparkles, Target, MessageCircle } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { Meeting, MeetingBrief } from "@/types";
import { Card, LoadingState, ErrorState, EmptyState, Button } from "@/components/ui/primitives";
import { PriorityBadge, FollowUpStatusBadge } from "@/components/ui/badge";

function formatDayLabel(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffDays = Math.round((d.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Tomorrow";
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
}

function MeetingBriefPanel({ meetingId }: { meetingId: number }) {
  const [brief, setBrief] = useState<MeetingBrief | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  function generate() {
    setOpen(true);
    setLoading(true);
    setError(null);
    api.meetings
      .brief(meetingId)
      .then(setBrief)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Couldn't generate the brief."))
      .finally(() => setLoading(false));
  }

  if (!open) {
    return (
      <button
        onClick={generate}
        className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-brass-dark hover:text-brass transition-colors"
      >
        <Sparkles size={13} /> Generate meeting brief
      </button>
    );
  }

  return (
    <div className="mt-3 rounded-lg border border-brass/25 bg-brass/5 px-4 py-3.5">
      {loading && <LoadingState label="Preparing your brief…" />}
      {error && (
        <div className="text-sm text-state-danger">
          {error}{" "}
          <button onClick={generate} className="underline underline-offset-2">
            Try again
          </button>
        </div>
      )}
      {brief && !loading && (
        <div className="space-y-3 text-sm">
          <div>
            <p className="text-xs uppercase tracking-wide text-brass-dark font-medium mb-1 flex items-center gap-1.5">
              <Target size={12} /> Objective
            </p>
            <p className="text-ink-900 italic">{brief.objective}</p>
          </div>

          {brief.talking_points.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-brass-dark font-medium mb-1 flex items-center gap-1.5">
                <MessageCircle size={12} /> Suggested talking points
              </p>
              <ul className="list-disc pl-4 space-y-0.5 text-ink-900">
                {brief.talking_points.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          )}

          {brief.open_tasks.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-ink-500 font-medium mb-1">Relevant open tasks</p>
              <ul className="space-y-1">
                {brief.open_tasks.map((t) => (
                  <li key={t.id} className="flex items-center justify-between text-ink-900">
                    <span>{t.title}</span>
                    <PriorityBadge priority={t.priority} />
                  </li>
                ))}
              </ul>
            </div>
          )}

          {brief.relevant_follow_ups.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-ink-500 font-medium mb-1">Relevant follow-ups</p>
              <ul className="space-y-1">
                {brief.relevant_follow_ups.map((f) => (
                  <li key={f.id} className="flex items-center justify-between text-ink-900">
                    <span>
                      {f.person} — {f.topic}
                    </span>
                    <FollowUpStatusBadge status={f.status} />
                  </li>
                ))}
              </ul>
            </div>
          )}

          {brief.pending_decisions.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-ink-500 font-medium mb-1">Pending decisions</p>
              <ul className="list-disc pl-4 space-y-0.5 text-ink-900">
                {brief.pending_decisions.map((d) => (
                  <li key={d.id}>{d.title}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setLoading(true);
    setError(null);
    api.meetings
      .list({ upcoming_only: true })
      .then(setMeetings)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not reach the server."))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  const grouped = meetings.reduce<Record<string, Meeting[]>>((acc, m) => {
    (acc[m.date] ||= []).push(m);
    return acc;
  }, {});

  return (
    <div className="px-8 py-8 max-w-4xl">
      <header className="mb-6">
        <h1 className="font-display text-3xl text-ink-900">Meetings</h1>
        <p className="mt-1 text-sm text-ink-500">Your upcoming schedule, prepped by your assistant.</p>
      </header>

      {loading && <LoadingState label="Loading meetings…" />}
      {error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && meetings.length === 0 && (
        <EmptyState
          icon={CalendarClock}
          title="Nothing on the calendar"
          description="No upcoming meetings found for this demo user."
        />
      )}

      {!loading &&
        !error &&
        Object.entries(grouped).map(([date, dayMeetings]) => (
          <div key={date} className="mb-7">
            <h2 className="mb-3 text-xs uppercase tracking-wide text-ink-500 font-medium">
              {formatDayLabel(date)}
            </h2>
            <div className="space-y-3">
              {dayMeetings.map((m) => (
                <Card key={m.id} className="p-5 flex items-start gap-5">
                  <div className="w-16 shrink-0 pt-0.5">
                    <span className="font-mono text-sm text-ink-700 font-medium">{m.time}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-ink-900">{m.title}</h3>
                    {m.description && <p className="mt-1 text-sm text-ink-500">{m.description}</p>}
                    <div className="mt-2 flex items-center gap-1.5 text-xs text-ink-500">
                      <Users size={13} />
                      {m.participants.join(", ")}
                    </div>
                    {m.notes && (
                      <p className="mt-3 rounded-md bg-surface px-3 py-2 text-xs text-ink-700 border border-surface-border">
                        <span className="font-medium text-brass-dark">Notes: </span>
                        {m.notes}
                      </p>
                    )}
                    <MeetingBriefPanel meetingId={m.id} />
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
    </div>
  );
}
