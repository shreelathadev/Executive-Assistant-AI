//frontend/lib/utils.ts
import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// export function formatDate(dateStr?: string | null): string {
//   if (!dateStr) return "—";
//   const d = new Date(dateStr + "T00:00:00");
//   return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
// }

export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "—";

  const dateOnly = dateStr.slice(0, 10);
  const d = new Date(`${dateOnly}T00:00:00`);

  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function isOverdue(dateStr?: string | null, status?: string): boolean {
  if (!dateStr || status === "completed") return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const d = new Date(dateStr + "T00:00:00");
  return d < today;
}

export function daysAgo(dateStr: string): number {
  const d = new Date(dateStr + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));
}
