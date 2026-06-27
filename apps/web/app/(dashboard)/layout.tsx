"use client";

// Each portal subfolder has its own layout.tsx composing AppShell (components/shell/app-shell.tsx)
// with that portal's nav (lib/navigation.ts). This outer layout just establishes the shared
// permission set once for every portal beneath it -- see hooks/use-permissions.ts and
// docs/RBAC.md. Phase 3: fetch the real granted-permission set server-side instead of the
// empty default (which renders nothing permission-gated, the safe default).
//
// Must be a Client Component: a Server Component can't pass a `Set` instance as a prop across
// the server/client boundary (RSC props must be serializable) -- constructing the Set here,
// client-side, avoids that entirely.

import { PermissionsProvider } from "@/hooks/use-permissions";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <PermissionsProvider value={new Set()}>{children}</PermissionsProvider>;
}
