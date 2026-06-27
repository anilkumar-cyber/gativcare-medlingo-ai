import { AppShell } from "@/components/shell/app-shell";

export default function SuperAdminLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="super-admin">{children}</AppShell>;
}
