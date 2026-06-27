import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

// Every list/table gets a designed empty state, never a blank table.
// See docs/UX_ARCHITECTURE.md#component-system.
export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-[var(--space-3)] py-[var(--space-12)] text-center",
        className,
      )}
    >
      {icon && <div className="text-[var(--color-fg-muted)]">{icon}</div>}
      <p className="text-[var(--text-base)] font-medium text-[var(--color-fg)]">{title}</p>
      {description && <p className="text-[var(--text-sm)] text-[var(--color-fg-muted)] max-w-sm">{description}</p>}
      {action}
    </div>
  );
}
