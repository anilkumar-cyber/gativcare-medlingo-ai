import { EmptyState } from "@/components/ui/empty-state";

// Reference implementation of the Coordinator Portal landing screen (New Leads pipeline) --
// see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal. Pipeline/CRM view lands in Phase 5.
export default function CoordinatorLeadsPage() {
  return <EmptyState title="No new leads" description="New inquiries will appear here for triage." />;
}
