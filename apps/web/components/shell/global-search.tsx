"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Searches across patients, doctors, hospitals, treatments, reports, appointments, messages,
 * invoices, documents, organizations, conversations, knowledge, settings. Scope is whatever the
 * caller's permissions already allow -- the API enforces this, not the component; this is a thin
 * input + results list. See docs/UX_ARCHITECTURE.md#navigation-system-every-portal.
 */
export function GlobalSearch({ className }: { className?: string }) {
  const [query, setQuery] = useState("");

  return (
    <div className={cn("relative flex items-center", className)}>
      <Search className="pointer-events-none absolute left-3 h-4 w-4 text-[var(--color-fg-muted)]" />
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search patients, doctors, hospitals, reports..."
        aria-label="Global search"
        className="h-10 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-subtle)] pl-9 pr-3 text-[var(--text-sm)] text-[var(--color-fg)] outline-none focus-visible:border-[var(--color-accent)]"
      />
    </div>
  );
}
