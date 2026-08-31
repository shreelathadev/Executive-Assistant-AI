"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { ApiError } from "@/lib/api";
import { Card, Button } from "@/components/ui/primitives";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login({ email, password });
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "Incorrect email or password."
          : "Couldn't reach the server. Try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="inline-block h-2 w-2 rounded-full bg-brass mb-2" />
          <h1 className="font-display italic text-2xl text-ink-900">Executive Assistant</h1>
          <p className="text-sm text-ink-500 mt-1">Welcome back.</p>
        </div>

        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-ink-700 mb-1">Email</label>
              <input
                type="email"
                required
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
              />
            </div>

            {error && <p className="text-sm text-state-danger">{error}</p>}

            <Button type="submit" disabled={loading} className="w-full justify-center">
              {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </Card>

        <p className="text-center text-sm text-ink-500 mt-4">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="text-brass-dark font-medium hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
