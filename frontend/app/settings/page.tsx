import { Card } from "@/components/ui/primitives";

export default function SettingsPage() {
  return (
    <div className="px-8 py-8 max-w-2xl">
      <header className="mb-6">
        <h1 className="font-display text-3xl text-ink-900">Settings</h1>
        <p className="mt-1 text-sm text-ink-500">Demo account details.</p>
      </header>
      <Card className="p-5 space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-ink-500">Name</span>
          <span className="text-ink-900 font-medium">Alex Morgan</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-500">Role</span>
          <span className="text-ink-900 font-medium">Founder, NovaTech</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-500">Email</span>
          <span className="text-ink-900 font-medium">alex@novatech.io</span>
        </div>
      </Card>
      <p className="mt-4 text-xs text-ink-500">
        This MVP uses a single demo user — no authentication yet, by design (see the 4-day scope).
      </p>
    </div>
  );
}
