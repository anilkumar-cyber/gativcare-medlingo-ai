import { JourneyCompanion } from "@/components/shell/journey-companion";
import { MetricCard } from "@/components/ui/metric-card";

// Reference implementation of the Patient Portal dashboard layout described in
// docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal -- Journey Companion front and center,
// not buried below widgets. Data below is placeholder pending Phase 3 API wiring.
export default function PatientDashboardPage() {
  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <JourneyCompanion
        currentStage="treatment_planning"
        nextAction={{ label: "Review your treatment quotation", href: "/patient/billing" }}
      />
      <div className="grid grid-cols-1 gap-[var(--space-4)] sm:grid-cols-3">
        <MetricCard label="Upcoming appointments" value="2" />
        <MetricCard label="Unread messages" value="3" />
        <MetricCard label="Pending documents" value="1" trend="Due in 3 days" trendDirection="down" />
      </div>
    </div>
  );
}
