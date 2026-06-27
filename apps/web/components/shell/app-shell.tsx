"use client";

import type { ReactNode } from "react";
import { GlobalSearch } from "@/components/shell/global-search";
import { CommandPalette } from "@/components/shell/command-palette";
import { NotificationCenter } from "@/components/shell/notification-center";
import { AIAssistantWidget } from "@/components/shell/ai-assistant-widget";
import { usePermissions } from "@/hooks/use-permissions";
import { PORTAL_NAV, type PortalKey } from "@/lib/navigation";

/**
 * The one layout every (dashboard)/<portal> composes: sidebar + top bar (search, notifications,
 * AI assistant, profile) + breadcrumbs + content. Differs per portal only in which nav items
 * render (lib/navigation.ts) -- not a different layout component. See docs/UX_ARCHITECTURE.md
 * #screen-hierarchy-by-portal.
 */
export function AppShell({
  portal,
  breadcrumbs,
  children,
}: {
  portal: PortalKey;
  breadcrumbs?: string[];
  children: ReactNode;
}) {
  const { has } = usePermissions();
  const items = PORTAL_NAV[portal].filter((item) => has(item.permission));

  return (
    <div className="flex min-h-screen bg-[var(--color-bg-subtle)]">
      <aside className="hidden w-64 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg)] p-[var(--space-4)] md:block">
        <nav aria-label={`${portal} navigation`}>
          <ul className="flex flex-col gap-[var(--space-1)]">
            {items.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="block rounded-[var(--radius-sm)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-fg-muted)] hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-fg)]"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <div className="flex-1">
        <header className="flex items-center justify-between gap-[var(--space-4)] border-b border-[var(--color-border)] bg-[var(--color-bg)] px-[var(--space-6)] py-[var(--space-3)]">
          <GlobalSearch className="max-w-md flex-1" />
          <div className="flex items-center gap-[var(--space-2)]">
            <NotificationCenter />
          </div>
        </header>

        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav aria-label="Breadcrumb" className="px-[var(--space-6)] py-[var(--space-2)] text-[var(--text-xs)] text-[var(--color-fg-muted)]">
            {breadcrumbs.join(" / ")}
          </nav>
        )}

        <main className="p-[var(--space-6)]">{children}</main>
      </div>

      <CommandPalette items={items} />
      <AIAssistantWidget context={{ pageLabel: breadcrumbs?.join(" / ") ?? portal }} />
    </div>
  );
}
