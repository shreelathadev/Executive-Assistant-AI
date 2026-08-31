"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { ApiError } from "@/lib/api";
import { Card, Button } from "@/components/ui/primitives";

export default function SignupPage() {
  const { signup } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await signup({
        name,
        email,
        password,
        company: company.trim() || undefined,
        role: role.trim() || undefined,
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError("An account with that email already exists.");
      } else if (err instanceof ApiError && err.status === 422) {
        setError("Password must be at least 8 characters, and email must be valid.");
      } else {
        setError("Couldn't reach the server. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="inline-block h-2 w-2 rounded-full bg-brass mb-2" />
          <h1 className="font-display italic text-2xl text-ink-900">Executive Assistant</h1>
          <p className="text-sm text-ink-500 mt-1">Your own AI assistant, set up in a minute.</p>
        </div>

        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-ink-700 mb-1">Name</label>
              <input
                required
                autoFocus
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-700 mb-1">Email</label>
              <input
                type="email"
                required
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
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
              />
              <p className="text-xs text-ink-500 mt-1">At least 8 characters.</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">Company (optional)</label>
                <input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">Role (optional)</label>
                <input
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full rounded-md border border-surface-border px-3 py-2 text-sm focus:border-brass"
                />
              </div>
            </div>

            {error && <p className="text-sm text-state-danger">{error}</p>}

            <Button type="submit" disabled={loading} className="w-full justify-center">
              {loading ? "Creating your account…" : "Create account"}
            </Button>
          </form>
        </Card>

        <p className="text-center text-sm text-ink-500 mt-4">
          Already have an account?{" "}
          <Link href="/login" className="text-brass-dark font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
