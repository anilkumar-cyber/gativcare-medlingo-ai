"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api-client";
import { setToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function OrgSignupPage() {
  const router = useRouter();
  const [orgName, setOrgName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token } = await api.orgSignup({
        org_name: orgName,
        owner_email: email,
        owner_password: password,
        owner_full_name: fullName || undefined,
      });
      setToken(access_token);
      router.push("/organization");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-subtle)]">
      <Card className="w-full max-w-sm">
        <h1 className="mb-[var(--space-6)] text-[var(--text-xl)] font-semibold">Create your organization</h1>
        <form onSubmit={onSubmit} className="flex flex-col gap-[var(--space-4)]">
          <input
            required
            placeholder="Organization name"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <input
            placeholder="Your full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <input
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <input
            type="password"
            required
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          {error && <p className="text-[var(--text-sm)] text-[var(--color-emergency)]">{error}</p>}
          <Button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create organization"}
          </Button>
          <a href="/login" className="text-center text-[var(--text-sm)] text-[var(--color-accent)]">
            Already have an account? Sign in
          </a>
        </form>
      </Card>
    </div>
  );
}
