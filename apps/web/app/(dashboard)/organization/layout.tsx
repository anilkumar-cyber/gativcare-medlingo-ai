import { AppShell } from "@/components/shell/app-shell";

export default function OrganizationLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="organization">{children}</AppShell>;
}
