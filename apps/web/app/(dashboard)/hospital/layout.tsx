import { AppShell } from "@/components/shell/app-shell";

export default function HospitalLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="hospital">{children}</AppShell>;
}
