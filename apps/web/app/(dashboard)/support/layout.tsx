import { AppShell } from "@/components/shell/app-shell";

export default function SupportLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="support">{children}</AppShell>;
}
