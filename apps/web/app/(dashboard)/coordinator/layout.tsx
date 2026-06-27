import { AppShell } from "@/components/shell/app-shell";

export default function CoordinatorLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="coordinator">{children}</AppShell>;
}
