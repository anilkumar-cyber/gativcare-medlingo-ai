import { AppShell } from "@/components/shell/app-shell";

export default function DoctorLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="doctor">{children}</AppShell>;
}
