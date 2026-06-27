import { MetricCard } from "@/components/ui/metric-card";

// Reference Admin Console landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function SuperAdminOverviewPage() {
  return (
    <div className="grid grid-cols-1 gap-[var(--space-4)] sm:grid-cols-3">
      <MetricCard label="Organizations" value="0" />
      <MetricCard label="Platform-wide users" value="0" />
      <MetricCard label="Active incidents" value="0" />
    </div>
  );
}
