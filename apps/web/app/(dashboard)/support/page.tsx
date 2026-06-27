import { EmptyState } from "@/components/ui/empty-state";

// Reference Support Portal landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function SupportTicketsPage() {
  return <EmptyState title="No open tickets" description="Support tickets will appear here." />;
}
