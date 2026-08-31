"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { PUBLIC_ROUTES } from "@/lib/AuthContext";

// Login/signup are full-bleed, no app chrome -- showing the task/meeting/
// assistant nav next to a login form would be confusing (and briefly
// showing it before the auth redirect kicks in looks like a flash of
// broken UI). Every other route gets the normal Sidebar + main layout.
export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);

  if (isPublicRoute) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
