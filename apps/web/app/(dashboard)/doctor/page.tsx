import { EmptyState } from "@/components/ui/empty-state";

// Reference Doctor Portal landing screen -- see docs/UX_ARCHITECTURE.md#screen-hierarchy-by-portal.
export default function DoctorTodayPage() {
  return <EmptyState title="No appointments today" description="Today's schedule will appear here." />;
}
