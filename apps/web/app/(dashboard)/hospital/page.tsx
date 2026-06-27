import { MetricCard } from "@/components/ui/metric-card";

// Reference Hospital Portal landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function HospitalOverviewPage() {
  return (
    <div className="grid grid-cols-1 gap-[var(--space-4)] sm:grid-cols-3">
      <MetricCard label="Beds occupied" value="0 / 0" />
      <MetricCard label="Admissions today" value="0" />
      <MetricCard label="International patients" value="0" />
    </div>
  );
}
