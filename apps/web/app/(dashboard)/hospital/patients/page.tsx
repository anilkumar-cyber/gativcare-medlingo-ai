"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Patient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function HospitalPatientsPage() {
  const [patients, setPatients] = useState<Patient[] | null>(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    api.listPatients().then(setPatients).catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"));
  }

  useEffect(load, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createPatient({ full_name: fullName, email: email || undefined, preferred_language: preferredLanguage || undefined });
      setFullName("");
      setEmail("");
      setPreferredLanguage("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create patient");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <Card>
        <CardHeader>
          <CardTitle>Register a patient</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onCreate} className="flex flex-wrap items-end gap-[var(--space-3)]">
            <input required placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input placeholder="Preferred language" value={preferredLanguage} onChange={(e) => setPreferredLanguage(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <Button type="submit" disabled={submitting}>{submitting ? "Registering..." : "Register patient"}</Button>
          </form>
          {error && <p className="mt-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Patients</CardTitle>
        </CardHeader>
        <CardContent>
          {patients === null ? (
            <div className="flex flex-col gap-[var(--space-2)]">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : patients.length === 0 ? (
            <EmptyState title="No patients yet" description="Register your first patient above." />
          ) : (
            <ul className="flex flex-col gap-[var(--space-2)]">
              {patients.map((p) => (
                <li key={p.id} className="flex items-center justify-between rounded-[var(--radius-sm)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)]">
                  <div>
                    <span className="text-[var(--text-sm)] text-[var(--color-fg)]">{p.full_name}</span>
                    <span className="ml-[var(--space-2)] text-[var(--text-xs)] text-[var(--color-fg-muted)]">{p.email}</span>
                  </div>
                  <a href={`/hospital/patients/${p.id}`} className={buttonVariants({ variant: "secondary", size: "sm" })}>
                    Manage case
                  </a>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
