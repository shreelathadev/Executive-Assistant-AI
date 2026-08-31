// frontend/app/settings/page.tsx
"use client";

import { Card } from "@/components/ui/primitives";
import { useAuth } from "@/lib/AuthContext";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="px-8 py-8 max-w-2xl">
      <header className="mb-6">
        <h1 className="font-display text-3xl text-ink-900">Settings</h1>
        <p className="mt-1 text-sm text-ink-500">Your account details.</p>
      </header>
      <Card className="p-5 space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-ink-500">Name</span>
          <span className="text-ink-900 font-medium">{user?.name ?? "—"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-500">Role</span>
          <span className="text-ink-900 font-medium">
            {user?.role ? (user?.company ? `${user.role}, ${user.company}` : user.role) : (user?.company ?? "—")}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-500">Email</span>
          <span className="text-ink-900 font-medium">{user?.email ?? "—"}</span>
        </div>
      </Card>
    </div>
  );
}