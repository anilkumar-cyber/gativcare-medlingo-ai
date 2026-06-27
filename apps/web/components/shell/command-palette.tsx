"use client";

import { useEffect, useState } from "react";
import { Dialog } from "@/components/ui/dialog";
import type { NavItem } from "@/lib/navigation";

/**
 * Cmd/Ctrl+K, fuzzy-jumps to any nav item or recent record. One instance mounted in AppShell,
 * not per-page. See docs/UX_ARCHITECTURE.md#navigation-system-every-portal.
 */
export function CommandPalette({ items }: { items: NavItem[] }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const matches = items.filter((item) => item.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <Dialog open={open} onClose={() => setOpen(false)} className="w-full max-w-lg">
      <input
        autoFocus
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Jump to..."
        aria-label="Command palette"
        className="mb-[var(--space-3)] w-full border-b border-[var(--color-border)] pb-[var(--space-2)] text-[var(--text-base)] outline-none"
      />
      <ul role="listbox" className="max-h-80 overflow-auto">
        {matches.map((item) => (
          <li key={item.href}>
            <a
              href={item.href}
              className="block rounded-[var(--radius-sm)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] hover:bg-[var(--color-bg-subtle)]"
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>
    </Dialog>
  );
}
