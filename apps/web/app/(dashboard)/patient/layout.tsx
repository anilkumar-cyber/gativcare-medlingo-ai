import { AppShell } from "@/components/shell/app-shell";

export default function PatientLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="patient">{children}</AppShell>;
}
