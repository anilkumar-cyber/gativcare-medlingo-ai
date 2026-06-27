"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Hospital } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function OrganizationHospitalsPage() {
  const [hospitals, setHospitals] = useState<Hospital[] | null>(null);
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    api.listHospitals().then(setHospitals).catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"));
  }

  useEffect(load, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createHospital({ name, city: city || undefined, country: country || undefined });
      setName("");
      setCity("");
      setCountry("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create hospital");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <Card>
        <CardHeader>
          <CardTitle>Add a hospital</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onCreate} className="flex flex-wrap items-end gap-[var(--space-3)]">
            <input required placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input placeholder="Country" value={country} onChange={(e) => setCountry(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <Button type="submit" disabled={submitting}>{submitting ? "Adding..." : "Add hospital"}</Button>
          </form>
          {error && <p className="mt-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Hospitals</CardTitle>
        </CardHeader>
        <CardContent>
          {hospitals === null ? (
            <div className="flex flex-col gap-[var(--space-2)]">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : hospitals.length === 0 ? (
            <EmptyState title="No hospitals yet" description="Add your first hospital above." />
          ) : (
            <ul className="flex flex-col gap-[var(--space-2)]">
              {hospitals.map((h) => (
                <li key={h.id} className="flex items-center justify-between rounded-[var(--radius-sm)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)]">
                  <span className="text-[var(--text-sm)] text-[var(--color-fg)]">{h.name}</span>
                  <span className="text-[var(--text-xs)] text-[var(--color-fg-muted)]">{[h.city, h.country].filter(Boolean).join(", ")}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
