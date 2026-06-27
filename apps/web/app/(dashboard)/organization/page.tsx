import { MetricCard } from "@/components/ui/metric-card";

// Reference Organization Portal landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function OrganizationOverviewPage() {
  return (
    <div className="grid grid-cols-1 gap-[var(--space-4)] sm:grid-cols-3">
      <MetricCard label="Hospitals" value="0" />
      <MetricCard label="Active users" value="0" />
      <MetricCard label="Monthly conversations" value="0" />
    </div>
  );
}
