import { AppShell } from "@/components/shell/app-shell";

export default function InterpreterLayout({ children }: { children: React.ReactNode }) {
  return <AppShell portal="interpreter">{children}</AppShell>;
}
