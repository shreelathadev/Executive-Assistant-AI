"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  ListChecks,
  CalendarClock,
  MessagesSquare,
  Scale,
  Sparkles,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutGrid },
  { href: "/tasks", label: "Tasks", icon: ListChecks },
  { href: "/meetings", label: "Meetings", icon: CalendarClock },
  { href: "/follow-ups", label: "Follow-ups", icon: MessagesSquare },
  { href: "/decisions", label: "Decisions", icon: Scale },
  { href: "/assistant", label: "Assistant", icon: Sparkles },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 shrink-0 bg-ink-900 text-white/90 flex flex-col min-h-screen">
      <div className="px-6 py-6 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-brass" />
          <span className="font-display italic text-lg tracking-tight text-white">
            Executive Assistant
          </span>
        </div>
        <p className="mt-1 text-xs text-white/45 font-body">
          For Alex Morgan · NovaTech
        </p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname?.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-white/10 text-white border-l-2 border-brass -ml-px pl-[11px]"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              )}
            >
              <Icon size={16} strokeWidth={2} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 py-4 border-t border-white/10">
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
            pathname === "/settings"
              ? "bg-white/10 text-white"
              : "text-white/60 hover:text-white hover:bg-white/5"
          )}
        >
          <Settings size={16} strokeWidth={2} />
          Settings
        </Link>
      </div>
    </aside>
  );
}
