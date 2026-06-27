import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// The building block of every dashboard's top row (Analytics module numbers, AI Accuracy
// Metrics, Translation Confidence, etc.) -- see docs/UX_ARCHITECTURE.md#component-system.
export function MetricCard({
  label,
  value,
  trend,
  trendDirection = "neutral",
}: {
  label: string;
  value: string;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
}) {
  const trendColor =
    trendDirection === "up"
      ? "text-[var(--color-success)]"
      : trendDirection === "down"
        ? "text-[var(--color-emergency)]"
        : "text-[var(--color-fg-muted)]";

  return (
    <Card>
      <p className="text-[var(--text-sm)] text-[var(--color-fg-muted)]">{label}</p>
      <p className="mt-[var(--space-2)] text-[var(--text-2xl)] font-semibold text-[var(--color-fg)]">{value}</p>
      {trend && <p className={cn("mt-[var(--space-1)] text-[var(--text-xs)]", trendColor)}>{trend}</p>}
    </Card>
  );
}
