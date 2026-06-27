"use client";

// Each portal subfolder has its own layout.tsx composing AppShell (components/shell/app-shell.tsx)
// with that portal's nav (lib/navigation.ts). This outer layout fetches the real granted
// permission set once (via /auth/me) and establishes it for every portal beneath it -- see
// hooks/use-permissions.ts and docs/RBAC.md. Unauthenticated visitors are redirected to /login.

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PermissionsProvider } from "@/hooks/use-permissions";
import { api } from "@/lib/api-client";
import { getToken } from "@/lib/auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [permissions, setPermissions] = useState<Set<string> | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api
      .me()
      .then((me) => setPermissions(new Set(me.permissions)))
      .catch(() => router.replace("/login"));
  }, [router]);

  if (permissions === null) {
    return <div className="flex min-h-screen items-center justify-center text-[var(--color-fg-muted)]">Loading...</div>;
  }

  return <PermissionsProvider value={permissions}>{children}</PermissionsProvider>;
}
