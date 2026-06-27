"use client";

// JWT stored in localStorage -- fine for this stage (single web app, no SSR-protected routes
// yet). Moving to an httpOnly cookie is a Phase-3-continued security hardening step, not a
// blocker for the app working end-to-end now.
const TOKEN_KEY = "gativcare_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
