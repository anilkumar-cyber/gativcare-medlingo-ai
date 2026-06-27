import { EmptyState } from "@/components/ui/empty-state";

// Reference Finance Portal landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function FinanceInvoicesPage() {
  return <EmptyState title="No invoices yet" description="Invoices will appear here as they're issued." />;
}
