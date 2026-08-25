"use client";

import { useEffect, useState } from "react";
import { MessagesSquare, Sparkles, Copy, Check } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { FollowUp } from "@/types";
import { Card, LoadingState, ErrorState, EmptyState, Button } from "@/components/ui/primitives";
import { FollowUpStatusBadge } from "@/components/ui/badge";
import { daysAgo, formatDate } from "@/lib/utils";

function FollowUpCard({ followUp }: { followUp: FollowUp }) {
  const [draft, setDraft] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.followUps.draft(followUp.id);
      setDraft(res.draft_message);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't draft a message.");
    } finally {
      setLoading(false);
    }
  }

  async function copy() {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(draft);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard access can fail silently in some browser contexts — not worth surfacing an error for
    }
  }

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-medium text-ink-900">
            {followUp.person}
            {followUp.organization && <span className="text-ink-500"> — {followUp.organization}</span>}
          </h3>
          <p className="text-sm text-ink-500 mt-0.5">{followUp.topic}</p>
          {followUp.notes && <p className="text-xs text-ink-500 mt-2 italic">{followUp.notes}</p>}
          <p className="text-xs text-ink-500 mt-2">
            Last contact {formatDate(followUp.last_contact_date)} · {daysAgo(followUp.last_contact_date)} days ago
          </p>
        </div>
        <FollowUpStatusBadge status={followUp.status} />
      </div>

      {followUp.status === "waiting" && (
        <div className="mt-3">
          {!draft && !loading && (
            <Button variant="secondary" onClick={generate}>
              <Sparkles size={14} /> Draft a follow-up
            </Button>
          )}
          {loading && <LoadingState label="Drafting…" />}
          {error && <p className="text-sm text-state-danger">{error}</p>}
          {draft && !loading && (
            <div className="rounded-md bg-brass/5 border border-brass/20 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-brass-dark font-medium mb-1.5">
                Draft — review before sending, nothing is sent automatically
              </p>
              <p className="text-sm text-ink-900 whitespace-pre-wrap">{draft}</p>
              <div className="mt-2.5 flex items-center gap-3">
                <button
                  onClick={copy}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-brass-dark hover:text-brass"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  {copied ? "Copied" : "Copy"}
                </button>
                <button onClick={generate} className="text-xs font-medium text-ink-500 hover:text-ink-700">
                  Regenerate
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default function FollowUpsPage() {
  const [followUps, setFollowUps] = useState<FollowUp[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setLoading(true);
    setError(null);
    api.followUps
      .list()
      .then(setFollowUps)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not reach the server."))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  return (
    <div className="px-8 py-8 max-w-4xl">
      <header className="mb-6">
        <h1 className="font-display text-3xl text-ink-900">Follow-ups</h1>
        <p className="mt-1 text-sm text-ink-500">Track who you&apos;re waiting on.</p>
      </header>

      {loading && <LoadingState label="Loading follow-ups…" />}
      {error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && followUps.length === 0 && (
        <EmptyState
          icon={MessagesSquare}
          title="Nothing to follow up on"
          description="You're not waiting on anyone right now."
        />
      )}

      {!loading && !error && followUps.length > 0 && (
        <div className="space-y-3">
          {followUps.map((f) => (
            <FollowUpCard key={f.id} followUp={f} />
          ))}
        </div>
      )}
    </div>
  );
}
