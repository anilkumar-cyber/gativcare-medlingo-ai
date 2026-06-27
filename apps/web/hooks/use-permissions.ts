"use client";

import { createContext, useContext } from "react";

/**
 * Permission strings come from docs/RBAC.md, fetched once at session start and held in this
 * context -- every gated UI element (nav item, settings section, button) checks against this,
 * never against a role name. Phase 3: PermissionsProvider fetches the real list from the API;
 * for now the context defaults to an empty set so nothing renders that shouldn't.
 */

const PermissionsContext = createContext<Set<string>>(new Set());

export const PermissionsProvider = PermissionsContext.Provider;

export function usePermissions() {
  const granted = useContext(PermissionsContext);
  return {
    has: (permission?: string) => !permission || granted.has(permission),
  };
}
