import { EmptyState } from "@/components/ui/empty-state";

// Reference Interpreter Console landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function InterpreterSessionsPage() {
  return <EmptyState title="No active sessions" description="Live interpretation sessions will appear here." />;
}
