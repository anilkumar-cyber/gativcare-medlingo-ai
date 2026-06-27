"use client";

import { useState } from "react";
import { Bell } from "lucide-react";
import { Dialog } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";

/**
 * One feed, filterable by type -- a notification is a rendered Event (docs/WORKFLOWS.md#event-catalog),
 * not a separate data model. Phase 3: fetched from a notifications endpoint backed by the same
 * event stream the Automation Agent subscribes to.
 */
export type NotificationItem = {
  id: string;
  type: "appointment" | "message" | "emergency" | "travel" | "visa" | "insurance" | "payment" | "ai_suggestion" | "system" | "approval" | "task";
  title: string;
  read: boolean;
};

const TYPE_VARIANT: Record<NotificationItem["type"], "neutral" | "accent" | "success" | "warning" | "emergency"> = {
  appointment: "accent",
  message: "neutral",
  emergency: "emergency",
  travel: "accent",
  visa: "accent",
  insurance: "accent",
  payment: "success",
  ai_suggestion: "accent",
  system: "neutral",
  approval: "warning",
  task: "neutral",
};

export function NotificationCenter({ items = [] as NotificationItem[] }: { items?: NotificationItem[] }) {
  const [open, setOpen] = useState(false);
  const unread = items.filter((i) => !i.read).length;

  return (
    <>
      <button
        aria-label={`Notifications${unread ? `, ${unread} unread` : ""}`}
        onClick={() => setOpen(true)}
        className="relative rounded-[var(--radius-md)] p-[var(--space-2)] hover:bg-[var(--color-bg-subtle)]"
      >
        <Bell className="h-5 w-5 text-[var(--color-fg)]" />
        {unread > 0 && (
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-[var(--color-emergency)]" />
        )}
      </button>
      <Dialog open={open} onClose={() => setOpen(false)} className="w-full max-w-md">
        <h2 className="mb-[var(--space-4)] text-[var(--text-lg)] font-semibold">Notifications</h2>
        {items.length === 0 ? (
          <EmptyState title="You're all caught up" description="New notifications will appear here." />
        ) : (
          <ul className="flex flex-col gap-[var(--space-2)]">
            {items.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-[var(--space-3)] rounded-[var(--radius-sm)] p-[var(--space-2)] hover:bg-[var(--color-bg-subtle)]">
                <span className="text-[var(--text-sm)]">{item.title}</span>
                <Badge variant={TYPE_VARIANT[item.type]}>{item.type.replace("_", " ")}</Badge>
              </li>
            ))}
          </ul>
        )}
      </Dialog>
    </>
  );
}
