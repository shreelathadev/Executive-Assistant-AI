"use client";

import { useEffect, useState } from "react";
import { Scale, Sparkles, Target, AlertTriangle, ListChecks } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { Decision } from "@/types";
import { Card, LoadingState, ErrorState, EmptyState, Button } from "@/components/ui/primitives";
import { DecisionStatusBadge } from "@/components/ui/badge";

function DecisionCard({ decision, onUpdated }: { decision: Decision; onUpdated: (d: Decision) => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const updated = await api.decisions.recommend(decision.id);
      onUpdated(updated);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't generate a recommendation.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-4">
        <h3 className="font-medium text-ink-900">{decision.title}</h3>
        <DecisionStatusBadge status={decision.status} />
      </div>
      {decision.context && <p className="text-sm text-ink-500 mt-1.5">{decision.context}</p>}
      {decision.options.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {decision.options.map((o) => (
            <span
              key={o}
              className="rounded-full border border-surface-border bg-surface px-2.5 py-0.5 text-xs text-ink-700"
            >
              {o}
            </span>
          ))}
        </div>
      )}

      {decision.ai_recommendation && (
        <div className="mt-3 rounded-md bg-brass/5 border border-brass/20 px-4 py-3 space-y-2.5">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-brass-dark uppercase tracking-wide">
              AI recommendation — final call is yours
            </p>
          </div>
          <div className="flex items-start gap-2">
            <Target size={14} className="text-brass-dark mt-0.5 shrink-0" />
            <p className="text-sm font-semibold text-ink-900">{decision.ai_recommendation.recommendation}</p>
          </div>
          <p className="text-sm text-ink-900">{decision.ai_recommendation.reasoning}</p>
          <div className="flex items-start gap-2 text-sm text-ink-700">
            <AlertTriangle size={13} className="mt-0.5 shrink-0 text-priority-high" />
            <span>{decision.ai_recommendation.risks}</span>
          </div>
          <div className="flex items-start gap-2 text-sm text-ink-700">
            <ListChecks size={13} className="mt-0.5 shrink-0 text-ink-500" />
            <span>{decision.ai_recommendation.factors}</span>
          </div>
          <button
            onClick={generate}
            disabled={loading}
            className="text-xs font-medium text-brass-dark hover:text-brass underline underline-offset-2"
          >
            {loading ? "Regenerating…" : "Regenerate"}
          </button>
        </div>
      )}

      {!decision.ai_recommendation && (
        <div className="mt-3">
          {loading ? (
            <LoadingState label="Weighing the options…" />
          ) : (
            <Button variant="secondary" onClick={generate}>
              <Sparkles size={14} /> Generate recommendation
            </Button>
          )}
          {error && <p className="mt-2 text-sm text-state-danger">{error}</p>}
        </div>
      )}
    </Card>
  );
}

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setLoading(true);
    setError(null);
    api.decisions
      .list()
      .then(setDecisions)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not reach the server."))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function handleUpdated(updated: Decision) {
    setDecisions((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
  }

  return (
    <div className="px-8 py-8 max-w-4xl">
      <header className="mb-6">
        <h1 className="font-display text-3xl text-ink-900">Decisions</h1>
        <p className="mt-1 text-sm text-ink-500">Pending calls, with an AI-backed recommendation.</p>
      </header>

      {loading && <LoadingState label="Loading decisions…" />}
      {error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && decisions.length === 0 && (
        <EmptyState icon={Scale} title="No decisions tracked" description="Nothing pending right now." />
      )}

      {!loading && !error && decisions.length > 0 && (
        <div className="space-y-3">
          {decisions.map((d) => (
            <DecisionCard key={d.id} decision={d} onUpdated={handleUpdated} />
          ))}
        </div>
      )}
    </div>
  );
}
